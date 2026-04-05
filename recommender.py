from collections import Counter
import re


class Recommender:
    def __init__(self):
        self.products = {}
        self.product_vectors = {}
        self._initialized = False
    
    def _tokenize(self, text):
        text = text.lower()
        words = re.findall(r'\w+', text)
        return [w for w in words if len(w) > 2]
    
    def _compute_tf(self, tokens):
        tf = Counter(tokens)
        total = len(tokens)
        return {word: count / total for word, count in tf.items()}
    
    def _compute_idf(self, documents):
        N = len(documents)
        idf = {}
        all_words = set(word for doc in documents for word in doc)
        for word in all_words:
            df = sum(1 for doc in documents if word in doc)
            idf[word] = (N / (df + 1))
        return idf
    
    def _compute_tfidf(self, tf, idf):
        return {word: tf_val * idf.get(word, 1) for word, tf_val in tf.items()}
    
    def _cosine_similarity(self, vec1, vec2):
        if not vec1 or not vec2:
            return 0.0
        
        common = set(vec1.keys()) & set(vec2.keys())
        if not common:
            return 0.0
        
        dot_product = sum(vec1[w] * vec2[w] for w in common)
        mag1 = sum(v ** 2 for v in vec1.values()) ** 0.5
        mag2 = sum(v ** 2 for v in vec2.values()) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def _build_vectors(self):
        from models import Product
        
        products = Product.query.all()
        self.products = {p.id: p for p in products}
        
        if not products:
            return
        
        tokens_list = []
        for p in products:
            text = f"{p.name} {p.description} {p.category}"
            tokens = self._tokenize(text)
            tokens_list.append(tokens)
        
        idf = self._compute_idf(tokens_list)
        
        for i, p in enumerate(products):
            tf = self._compute_tf(tokens_list[i])
            self.product_vectors[p.id] = self._compute_tfidf(tf, idf)
    
    def _get_action_weights(self):
        return {
            'view': 1.0,
            'like': 2.0,
            'buy': 3.0
        }
    
    def _get_user_profile_vector(self, user_id):
        from models import UserAction
        
        actions = UserAction.query.filter_by(user_id=user_id).all()
        
        if not actions:
            return None
        
        weights = self._get_action_weights()
        profile = Counter()
        total_weight = 0
        
        action_counts = Counter(a.product_id for a in actions)
        
        for action in actions:
            if action.product_id not in self.product_vectors:
                continue
            
            weight = weights.get(action.action_type, 1.0)
            
            view_count = action_counts.get(action.product_id, 1)
            if action.action_type == 'view':
                weight *= min(view_count, 3)
            
            if action.rating:
                weight *= (action.rating / 5.0)
            
            for word, value in self.product_vectors[action.product_id].items():
                profile[word] += value * weight
            total_weight += weight
        
        if total_weight > 0:
            for word in profile:
                profile[word] /= total_weight
        
        return dict(profile)
    
    def get_recommendations(self, user_id, n=6):
        self._ensure_initialized()
        user_vector = self._get_user_profile_vector(user_id)
        
        if user_vector is None:
            return self._get_popular_products(n)
        
        from models import UserAction
        
        viewed_products = set(
            a.product_id for a in UserAction.query.filter_by(user_id=user_id).all()
        )
        
        product_scores = []
        for product_id in self.products:
            if product_id not in viewed_products:
                sim = self._cosine_similarity(
                    user_vector, 
                    self.product_vectors.get(product_id, {})
                )
                product_scores.append((self.products[product_id], sim))
        
        product_scores.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in product_scores[:n]]
    
    def _get_popular_products(self, n=6):
        from models import Product
        return Product.query.order_by(Product.rating.desc()).limit(n).all()
    
    def get_similar_products(self, product_id, n=4):
        self._ensure_initialized()
        if product_id not in self.product_vectors:
            return []
        
        similar = []
        target_vector = self.product_vectors[product_id]
        
        for pid in self.products:
            if pid != product_id:
                sim = self._cosine_similarity(
                    target_vector, 
                    self.product_vectors.get(pid, {})
                )
                similar.append((self.products[pid], sim))
        
        similar.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in similar[:n]]
    
    def _ensure_initialized(self):
        if not self._initialized:
            self._build_vectors()
            self._initialized = True
    
    def refresh(self):
        self._build_vectors()


recommender = Recommender()
