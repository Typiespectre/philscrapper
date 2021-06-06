import re

# text에서 phil_types의 keywords 중 문자열의 일부에 맞는 단어가 있을 경우 tag를 한다.
# keywords 참조 : https://m.blog.naver.com/PostView.nhn?blogId=sgjjojo&logNo=221184479000&proxyReferer=https:%2F%2Fwww.google.com%2F

Aesthetics = ["Aesthetics"]
Epistemology = [
    "Epistemology",
    "causality",
    "freewill",
    "determinism",
    "teleology",
    "anthropology",
]
Ethics = ["Ethics", "moral", "political"]
Logic = [
    "Logic",
    "deduction",
    "induction",
    "dialectic",
    "mathematical",
    "demonstration",
    "analogy",
]
Metaphysics = [
    "Metaphysics",
    "methodology",
    "ontology",
    "cosmology",
]
Eastern = ["Eastern", "chinese", "japan", "korean", "buddhist", "indian"]
Minds = ["Minds", "psychology", "physicalism", "machine", "consciousness", "mentality"]

phil_types = [Aesthetics, Epistemology, Ethics, Logic, Metaphysics, Eastern, Minds]


def tagging(text):
    tags = []
    words = []
    words_count = {}
    for types in phil_types:
        for keywords in types:
            """
            if re.search(keywords[:5], text, re.IGNORECASE):
                if types[0] not in tags:
                    tags.append(types[0])
            """
            word_found = re.findall(keywords[:5], text, re.IGNORECASE)
            if len(word_found) != 0:
                words += word_found
    if len(words) == 0:
        words.append("others")
    # text 내에서 발견된 keyword의 종류와 개수 찾기
    for i in words:
        i = i.lower()
        try:
            words_count[i] += 1
        except:
            words_count[i] = 1
    # text 내 전체 keyword의 평균 개수 미만 keyword는 포함하지 않음
    keyword_average = sum(words_count.values()) // len(words_count)
    for keys, values in words_count.items():
        if values > keyword_average:
            for types in phil_types:
                for keywords in types:
                    if keys == keywords[:5]:
                        tags.append(types[0])
    if len(tags) == 0:
        tags.append("others")
    # tag 중복 제거
    tag_set = set(tags)
    tag_list = list(tag_set)
    tag = ", ".join(tag_list)
    return tag