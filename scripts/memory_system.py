#!/usr/bin/env python3
"""
OpenClaw Memory System v2 - 简化版
- 使用jieba分词 + TF-IDF (无需下载模型)
- BM25关键词匹配
- 时间衰减
- MMR去重
"""
import os
import json
import time
import math
import pickle
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict

import jieba
import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 配置
WORKSPACE = Path("/Users/xs/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_MD = WORKSPACE / "MEMORY.md"
INDEX_DIR = WORKSPACE / ".memory_index"
INDEX_DIR.mkdir(exist_ok=True)

# 检索参数
TFIDF_WEIGHT = 0.6   # TF-IDF权重
BM25_WEIGHT = 0.4    # BM25权重
TIME_DECAY_DAYS = 30  # 时间衰减周期
MMR_LAMBDA = 0.7     # MMR多样性参数

class MemorySystem:
    def __init__(self):
        self.documents = []
        self.metadata = []
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.bm25 = None
        
    def load_memories(self):
        """加载所有记忆文件"""
        print("📚 加载记忆文件...")
        
        docs = []
        meta = []
        
        # 加载MEMORY.md
        if MEMORY_MD.exists():
            with open(MEMORY_MD, 'r', encoding='utf-8') as f:
                content = f.read()
                paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p.strip()) > 10]
                for i, para in enumerate(paragraphs):
                    docs.append(para)
                    meta.append({
                        'source': 'MEMORY.md',
                        'index': i,
                        'timestamp': MEMORY_MD.stat().st_mtime,
                        'type': 'long_term'
                    })
        
        # 加载memory/*.md
        if MEMORY_DIR.exists():
            for md_file in sorted(MEMORY_DIR.glob('*.md')):
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p.strip()) > 10]
                    for i, para in enumerate(paragraphs):
                        docs.append(para)
                        meta.append({
                            'source': md_file.name,
                            'index': i,
                            'timestamp': md_file.stat().st_mtime,
                            'type': 'daily'
                        })
        
        self.documents = docs
        self.metadata = meta
        print(f"✅ 加载了 {len(docs)} 个记忆片段")
    
    def build_tfidf_index(self):
        """构建TF-IDF索引"""
        print("🔨 构建TF-IDF索引...")
        
        if not self.documents:
            print("⚠️ 没有文档")
            return
        
        # 使用jieba分词
        def tokenize(text):
            return ' '.join(jieba.cut(text))
        
        tokenized_docs = [tokenize(doc) for doc in self.documents]
        
        # 构建TF-IDF
        self.tfidf_vectorizer = TfidfVectorizer(max_features=5000)
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(tokenized_docs)
        
        # 保存索引
        with open(INDEX_DIR / "tfidf.pkl", 'wb') as f:
            pickle.dump({
                'vectorizer': self.tfidf_vectorizer,
                'matrix': self.tfidf_matrix,
                'documents': self.documents,
                'metadata': self.metadata
            }, f)
        
        print(f"✅ TF-IDF索引已构建: {self.tfidf_matrix.shape}")
    
    def build_bm25_index(self):
        """构建BM25索引"""
        print("🔨 构建BM25索引...")
        
        if not self.documents:
            print("⚠️ 没有文档")
            return
        
        # jieba分词
        tokenized_docs = [list(jieba.cut(doc)) for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        
        # 保存
        with open(INDEX_DIR / "bm25.pkl", 'wb') as f:
            pickle.dump(self.bm25, f)
        
        print(f"✅ BM25索引已构建")
    
    def load_index(self):
        """加载已有索引"""
        try:
            with open(INDEX_DIR / "tfidf.pkl", 'rb') as f:
                data = pickle.load(f)
                self.tfidf_vectorizer = data['vectorizer']
                self.tfidf_matrix = data['matrix']
                self.documents = data['documents']
                self.metadata = data['metadata']
            
            with open(INDEX_DIR / "bm25.pkl", 'rb') as f:
                self.bm25 = pickle.load(f)
            
            print(f"✅ 索引已加载: {len(self.documents)} 个文档")
            return True
        except:
            return False
    
    def time_decay_score(self, timestamp: float) -> float:
        """时间衰减分数"""
        now = time.time()
        days_ago = (now - timestamp) / 86400
        return math.exp(-days_ago / TIME_DECAY_DAYS)
    
    def mmr_rerank(self, query_vec, candidates: List[Tuple[int, float]], 
                   top_k: int = 10) -> List[Tuple[int, float]]:
        """MMR重排序"""
        if len(candidates) <= top_k:
            return candidates
        
        selected = []
        candidate_indices = [idx for idx, _ in candidates]
        candidate_scores = {idx: score for idx, score in candidates}
        
        # 获取候选文档向量
        candidate_vecs = self.tfidf_matrix[candidate_indices]
        
        while len(selected) < top_k and candidate_indices:
            best_score = -float('inf')
            best_idx = None
            best_pos = None
            
            for pos, idx in enumerate(candidate_indices):
                # 相关性
                relevance = candidate_scores[idx]
                
                # 多样性
                if selected:
                    selected_vecs = self.tfidf_matrix[selected]
                    current_vec = self.tfidf_matrix[idx]
                    similarities = cosine_similarity(current_vec, selected_vecs)[0]
                    max_sim = similarities.max()
                else:
                    max_sim = 0
                
                # MMR分数
                mmr_score = MMR_LAMBDA * relevance - (1 - MMR_LAMBDA) * max_sim
                
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = idx
                    best_pos = pos
            
            if best_idx is not None:
                selected.append(best_idx)
                candidate_indices.pop(best_pos)
        
        return [(idx, candidate_scores[idx]) for idx in selected]
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """混合检索"""
        if not self.documents:
            if not self.load_index():
                self.load_memories()
                self.build_tfidf_index()
                self.build_bm25_index()
        
        # 1. TF-IDF检索
        def tokenize(text):
            return ' '.join(jieba.cut(text))
        
        query_tokenized = tokenize(query)
        query_vec = self.tfidf_vectorizer.transform([query_tokenized])
        tfidf_scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        
        # 2. BM25检索
        query_tokens = list(jieba.cut(query))
        bm25_scores = self.bm25.get_scores(query_tokens)
        
        # 归一化BM25
        max_bm25 = bm25_scores.max() if bm25_scores.max() > 0 else 1
        bm25_scores_norm = bm25_scores / max_bm25
        
        # 3. 混合分数 + 时间衰减
        combined_scores = {}
        for idx in range(len(self.documents)):
            hybrid_score = TFIDF_WEIGHT * tfidf_scores[idx] + BM25_WEIGHT * bm25_scores_norm[idx]
            time_score = self.time_decay_score(self.metadata[idx]['timestamp'])
            final_score = hybrid_score * (0.7 + 0.3 * time_score)
            combined_scores[idx] = final_score
        
        # 4. 排序
        sorted_candidates = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        top_candidates = sorted_candidates[:top_k * 2]
        
        # 5. MMR重排序
        final_results = self.mmr_rerank(query_vec, top_candidates, top_k)
        
        # 6. 构建返回结果
        results = []
        for idx, score in final_results:
            results.append({
                'content': self.documents[idx],
                'score': float(score),
                'source': self.metadata[idx]['source'],
                'index': self.metadata[idx]['index'],
                'type': self.metadata[idx]['type'],
                'timestamp': self.metadata[idx]['timestamp'],
                'date': datetime.fromtimestamp(self.metadata[idx]['timestamp']).strftime('%Y-%m-%d')
            })
        
        return results
    
    def rebuild_index(self):
        """重建索引"""
        print("🔄 重建记忆索引...")
        self.load_memories()
        self.build_tfidf_index()
        self.build_bm25_index()
        print("✅ 索引重建完成")
    
    def flush_memory(self):
        """Memory Flush - 整理记忆"""
        print("🧹 开始Memory Flush...")
        
        # 1. 加载所有记忆
        self.load_memories()
        
        # 2. 按时间分组
        recent = []  # 最近7天
        medium = []  # 7-30天
        old = []     # 30天以上
        
        now = time.time()
        for i, meta in enumerate(self.metadata):
            days_ago = (now - meta['timestamp']) / 86400
            doc = self.documents[i]
            
            if days_ago <= 7:
                recent.append((doc, meta))
            elif days_ago <= 30:
                medium.append((doc, meta))
            else:
                old.append((doc, meta))
        
        print(f"📊 记忆分布: 最近7天={len(recent)}, 7-30天={len(medium)}, 30天以上={len(old)}")
        
        # 3. 对旧记忆进行压缩（提取关键信息）
        if len(old) > 100:
            print(f"⚠️ 旧记忆过多({len(old)}个)，建议手动整理MEMORY.md")
        
        # 4. 重建索引
        self.rebuild_index()
        
        print("✅ Memory Flush完成")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 memory_system.py build          # 构建索引")
        print("  python3 memory_system.py search <query> # 搜索")
        print("  python3 memory_system.py flush          # Memory Flush")
        sys.exit(1)
    
    action = sys.argv[1]
    memory = MemorySystem()
    
    if action == 'build':
        memory.load_memories()
        memory.build_tfidf_index()
        memory.build_bm25_index()
        
    elif action == 'search':
        if len(sys.argv) < 3:
            print("请提供搜索关键词")
            sys.exit(1)
        
        query = ' '.join(sys.argv[2:])
        results = memory.search(query, top_k=5)
        
        print(f"\n🔍 搜索: {query}")
        print(f"{'='*60}")
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. [{result['source']}] 分数: {result['score']:.3f}")
            print(f"   日期: {result['date']}")
            print(f"   内容: {result['content'][:200]}...")
    
    elif action == 'flush':
        memory.flush_memory()
    
    else:
        print(f"未知操作: {action}")
        sys.exit(1)

if __name__ == '__main__':
    main()
