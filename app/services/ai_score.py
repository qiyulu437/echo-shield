# open port for later machine learning scores

from __future__ import annotations

from typing import Iterable, Sequence, Tuple, List

from app.rules import keywords as kw

def _normalize_text(text: str | None) -> str:
    return (text or "").lower()

def _hit_keywords(text: str, candidates: Iterable[str]) -> List[str]:
    # return hit words 
    text = text.lower()
    hits: List[str] = []
    for k in candidates:
        k_low = k.lower()
        if k_low and k_low in text:
            hits.append(k_low)
    
    return list(dict.fromkeys(hits))

def score_from_meta(
    title: str | None,
    description: str | None,
    tags: Sequence[str] | None,
    duration_seconds: int | None,
    category_id: str | None,
    channel_title: str | None,
    comments: Sequence[str] | None = None,
) -> Tuple[float, int, List[str]]: 

## Calculate ai_scores from metadata
## ai_meta_scoes : float [0,1]
## total_hits : int
## hit_list : List[str] remove the overlapped keywords

    title_t = _normalize_text(title)
    desc_t = _normalize_text(description)
    tags = tags or []
    tags_t = " ".join(tags).lower()
    channel_t = _normalize_text(channel_title)
    
    base_text = " ".join(filter(None, [title_t, desc_t, tags_t]))
    
    hits_core = _hit_keywords(base_text, kw.AI_CORE)
    hits_media = _hit_keywords(base_text, kw.AI_MEDIA)
    hits_scam = _hit_keywords(base_text, kw.SCAM)
    hits_politics = _hit_keywords(base_text, kw.POLITICS)
    hits_clickbait = _hit_keywords(base_text, kw.CLICKBAIT)
    hits_hashtags = _hit_keywords(tags_t, kw.HASHTAGS)
    
    comment_hits: List[str] = []
    if comments:
        comment_text = " ".join([_normalize_text(c) for c in comments])
        comment_hits = _hit_keywords(
            comment_text, kw.AI_CORE | kw.SCAM | kw.AI_MEDIA
        )
    
    # filtered hit list 
    hit_list_all: List[str] = []
    for group in [hits_core, hits_media, hits_scam, hits_politics,
                  hits_clickbait, hits_hashtags, comment_hits]:
        for h in group:
            if h not in hit_list_all:
                hit_list_all.append(h)

    total_hits = len(hit_list_all)
    
    def clamp01(x: float) -> float:
        return max(0.0, min(1.0, x))
    
    kw_core_score = clamp01(len(hits_core) / 3.0)          # max keywords : 3
    kw_media_score = clamp01(len(hits_media) / 2.0)
    kw_scam_score = clamp01(len(hits_scam) / 2.0)
    kw_politics_score = clamp01(len(hits_politics) / 2.0)
    kw_clickbait_score = clamp01(len(hits_clickbait) / 3.0)
    kw_tags_score = clamp01(len(hits_hashtags) / 2.0)
    comment_score = clamp01(len(comment_hits) / 3.0)
    
    duration_term = 0.0
    if duration_seconds is not None:
        if duration_seconds <= 180: # short video easier go viral
            duration_term = 0.1
        if duration_seconds > 180:
            duration_term = -0.1 # longer video less likely to be AI-made
            
    category_term = 0.0
    # YouTube: 10=Music, 24=Entertainment, 25=News & Politics
    if category_id == "10":
        if not hits_media:
            category_term = -0.15 # normal MV
    elif category_id in {"25", "29"}: # News & Politics / Nonprofits & Activism
        category_term = 0.05

    channel_term = 0.0
    if "ai" in channel_t:
        channel_term += 0.05
        
    raw_score = (
        0.45 * kw_core_score
        + 0.15 * max(kw_media_score, kw_scam_score)
        + 0.10 * kw_politics_score
        + 0.05 * kw_clickbait_score
        + 0.20 * kw_tags_score
        + 0.20 * comment_score
        + duration_term
        + category_term
        + channel_term
    ) # adjust it later 
    
    ai_meta_score = clamp01(raw_score)
    
    return ai_meta_score, total_hits, hit_list_all
