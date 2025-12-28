def extract_result(data):
    """
    Extracts evaluation results from the given data.

    This function categorizes words based on pronunciation accuracy
    into high, medium, and low accuracy words. It also extracts the
    total suggested score, pronunciation accuracy, and fluency.

    Args:
        data (dict): A dictionary containing evaluation results.

    Returns:
        dict: A dictionary containing extracted results including
        total scores and categorized words.
    """

    # 提取总分数、准确性、流畅度
    suggested_score = data[0]["result"]["SuggestedScore"]
    pron_accuracy = data[0]["result"]["PronAccuracy"]
    pron_fluency = data[0]["result"]["PronFluency"]

    # 提取发音准确性不同范围的单词
    LOW_ACCURACY_THRESHOLD = 50
    HIGH_ACCURACY_THRESHOLD = 80

    high_accuracy_words = []
    medium_accuracy_words = []
    low_accuracy_words = []

    for word_info in data[0]["result"]["Words"]:
        word = word_info["Word"]
        accuracy = word_info["PronAccuracy"]

        # 分类单词
        if accuracy >= HIGH_ACCURACY_THRESHOLD:
            high_accuracy_words.append(word)
        elif LOW_ACCURACY_THRESHOLD < accuracy < HIGH_ACCURACY_THRESHOLD:
            medium_accuracy_words.append(word)
        else:
            low_accuracy_words.append(word)

    result = {
        "TotalSuggestedScore": suggested_score,
        "TotalPronAccuracy": pron_accuracy,
        "TotalPronFluency": pron_fluency,
        "HighAccuracyWords": filter_low_accuracy_words(high_accuracy_words),
        "MediumAccuracyWords": filter_low_accuracy_words(medium_accuracy_words),
        "LowAccuracyWords": filter_low_accuracy_words(low_accuracy_words)
    }

    return result

def filter_low_accuracy_words(low_accuracy_words):

   # 扩展版英语语法功能词列表
    FILTER_WORDS = {
    # 冠词 (Articles)
    "a", "an", "the",
    
    # 介词 (Prepositions)
    "aboard", "about", "above", "across", "after", "against", "along", "amid",
    "among", "around", "as", "at", "before", "behind", "below", "beneath",
    "beside", "between", "beyond", "by", "concerning", "despite", "down",
    "during", "except", "for", "from", "in", "inside", "into", "like", "near",
    "of", "off", "on", "onto", "out", "outside", "over", "past", "regarding",
    "round", "since", "through", "throughout", "to", "toward", "under",
    "underneath", "until", "unto", "up", "upon", "with", "within", "without",
    
    # 代词 (Pronouns)
    "i", "me", "my", "mine", "myself",
    "you", "your", "yours", "yourself", "yourselves",
    "he", "him", "his", "himself",
    "she", "her", "hers", "herself",
    "it", "its", "itself",
    "we", "us", "our", "ours", "ourselves",
    "they", "them", "their", "theirs", "themselves",
    "this", "that", "these", "those",
    "who", "whom", "whose", "which", "what",
    
    # 连词 (Conjunctions)
    "and", "but", "or", "nor", "for", "yet", "so",
    "after", "although", "as", "because", "before", "if", "since", "than",
    "though", "unless", "until", "when", "where", "whether", "while",
    
    # 助动词/系动词 (Auxiliary/Copula verbs)
    "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing",
    "can", "could", "may", "might", "shall", "should", "will", "would", "must",
    
    # 限定词 (Determiners)
    "all", "another", "any", "both", "each", "either", "enough", "every",
    "few", "fewer", "little", "many", "more", "most", "much", "neither",
    "no", "other", "several", "some", "such",
    
    # 其他功能词
    "there", "here", "not", "only", "very", "too", "just", "also",
    "even", "rather", "quite", "almost", "enough", "really", "perhaps",
    "maybe", "actually", "basically", "certainly", "definitely", "probably",
    
    # 缩写形式
    "'s", "'re", "'m", "'d", "'ll", "'ve", "n't"
    }

    """过滤掉停用词，保留需要教学的重点词汇"""
    return [
        word_info for word_info in low_accuracy_words 
        if word_info.lower() not in FILTER_WORDS 
    ]

# 测试数据
data = {
    "code": 0,
    "message": "20a1f323-a26b-49db-8859-e7e602dac38e_37",
    "voice_id": "20a1f323-a26b-49db-8859-e7e602dac38e",
    "result": {
        "SuggestedScore": 68.75,
        "PronAccuracy": 68.75,
        "PronFluency": 0.92,
        "PronCompletion": 1,
        "Words": [
            {
                "MemBeginTime": 450,
                "MemEndTime": 1320,
                "PronAccuracy": 91.27,
                "PronFluency": 0.95,
                "ReferenceWord": "hello_0",
                "Word": "hello",
                "MatchTag": 0,
                "KeywordTag": 0,
                "PhoneInfos": [
                    {
                        "MemBeginTime": 450,
                        "MemEndTime": 590,
                        "PronAccuracy": 85.79,
                        "DetectedStress": False,
                        "Phone": "hh",
                        "ReferencePhone": "",
                        "ReferenceLetter": "",
                        "Stress": False,
                        "MatchTag": 0
                    },
                    {
                        "MemBeginTime": 590,
                        "MemEndTime": 810,
                        "PronAccuracy": 88.63,
                        "DetectedStress": False,
                        "Phone": "ah",
                        "ReferencePhone": "",
                        "ReferenceLetter": "",
                        "Stress": False,
                        "MatchTag": 0
                    },
                    {
                        "MemBeginTime": 810,
                        "MemEndTime": 930,
                        "PronAccuracy": 92.69,
                        "DetectedStress": False,
                        "Phone": "l",
                        "ReferencePhone": "",
                        "ReferenceLetter": "",
                        "Stress": True,
                        "MatchTag": 0
                    },
                    {
                        "MemBeginTime": 930,
                        "MemEndTime": 1320,
                        "PronAccuracy": 94.27,
                        "DetectedStress": False,
                        "Phone": "ow",
                        "ReferencePhone": "",
                        "ReferenceLetter": "",
                        "Stress": False,
                        "MatchTag": 0
                    }
                ],
                "Tone": {
                    "Valid": False,
                    "RefTone": -1,
                    "HypothesisTone": -1
                }
            },
            {
                "MemBeginTime": 1400,
                "MemEndTime": 2100,
                "PronAccuracy": 72.35,
                "PronFluency": 0.88,
                "ReferenceWord": "world_1",
                "Word": "world",
                "MatchTag": 0,
                "KeywordTag": 0,
                "PhoneInfos": [
                    {
                        "MemBeginTime": 1400,
                        "MemEndTime": 1550,
                        "PronAccuracy": 65.42,
                        "DetectedStress": False,
                        "Phone": "w",
                        "ReferencePhone": "",
                        "ReferenceLetter": "",
                        "Stress": False,
                        "MatchTag": 0
                    },
                    {
                        "MemBeginTime": 1550,
                        "MemEndTime": 1750,
                        "PronAccuracy": 68.31,
                        "DetectedStress": False,
                        "Phone": "er",
                        "ReferencePhone": "",
                        "ReferenceLetter": "",
                        "Stress": False,
                        "MatchTag": 0
                    },
                    {
                        "MemBeginTime": 1750,
                        "MemEndTime": 1900,
                        "PronAccuracy": 75.89,
                        "DetectedStress": False,
                        "Phone": "l",
                        "ReferencePhone": "",
                        "ReferenceLetter": "",
                        "Stress": True,
                        "MatchTag": 0
                    },
                    {
                        "MemBeginTime": 1900,
                        "MemEndTime": 2100,
                        "PronAccuracy": 79.78,
                        "DetectedStress": False,
                        "Phone": "d",
                        "ReferencePhone": "",
                        "ReferenceLetter": "",
                        "Stress": False,
                        "MatchTag": 0
                    }
                ],
                "Tone": {
                    "Valid": False,
                    "RefTone": -1,
                    "HypothesisTone": -1
                }
            },
            {
                "MemBeginTime": 2200,
                "MemEndTime": 2900,
                "PronAccuracy": 42.56,
                "PronFluency": 0.76,
                "ReferenceWord": "python_2",
                "Word": "python",
                "MatchTag": 0,
                "KeywordTag": 0,
                "PhoneInfos": [
                    {
                        "MemBeginTime": 2200,
                        "MemEndTime": 2350,
                        "PronAccuracy": 38.42,
                        "DetectedStress": False,
                        "Phone": "p",
                        "ReferencePhone": "",
                        "ReferenceLetter": "",
                        "Stress": False,
                        "MatchTag": 0
                    },
                    {
                        "MemBeginTime": 2350,
                        "MemEndTime": 2550,
                        "PronAccuracy": 45.31,
                        "DetectedStress": False,
                        "Phone": "ai",
                        "ReferencePhone": "",
                        "ReferenceLetter": "",
                        "Stress": False,
                        "MatchTag": 0
                    },
                    {
                        "MemBeginTime": 2550,
                        "MemEndTime": 2700,
                        "PronAccuracy": 40.89,
                        "DetectedStress": False,
                        "Phone": "th",
                        "ReferencePhone": "",
                        "ReferenceLetter": "",
                        "Stress": True,
                        "MatchTag": 0
                    },
                    {
                        "MemBeginTime": 2700,
                        "MemEndTime": 2900,
                        "PronAccuracy": 45.62,
                        "DetectedStress": False,
                        "Phone": "n",
                        "ReferencePhone": "",
                        "ReferenceLetter": "",
                        "Stress": False,
                        "MatchTag": 0
                    }
                ],
                "Tone": {
                    "Valid": False,
                    "RefTone": -1,
                    "HypothesisTone": -1
                }
            },
            {
                "MemBeginTime": 3000,
                "MemEndTime": 3800,
                "PronAccuracy": 68.92,
                "PronFluency": 0.91,
                "ReferenceWord": "programming_3",
                "Word": "programming",
                "MatchTag": 0,
                "KeywordTag": 0,
                "PhoneInfos": [
                    {
                        "MemBeginTime": 3000,
                        "MemEndTime": 3200,
                        "PronAccuracy": 65.78,
                        "DetectedStress": False,
                        "Phone": "p",
                        "ReferencePhone": "",
                        "ReferenceLetter": "",
                        "Stress": False,
                        "MatchTag": 0
                    },
                    {
                        "MemBeginTime": 3200,
                        "MemEndTime": 3400,
                        "PronAccuracy": 70.31,
                        "DetectedStress": False,
                        "Phone": "r",
                        "ReferencePhone": "",
                        "ReferenceLetter": "",
                        "Stress": False,
                        "MatchTag": 0
                    },
                    {
                        "MemBeginTime": 3400,
                        "MemEndTime": 3600,
                        "PronAccuracy": 72.45,
                        "DetectedStress": False,
                        "Phone": "ow",
                        "ReferencePhone": "",
                        "ReferenceLetter": "",
                        "Stress": True,
                        "MatchTag": 0
                    },
                    {
                        "MemBeginTime": 3600,
                        "MemEndTime": 3800,
                        "PronAccuracy": 67.14,
                        "DetectedStress": False,
                        "Phone": "m",
                        "ReferencePhone": "",
                        "ReferenceLetter": "",
                        "Stress": False,
                        "MatchTag": 0
                    }
                ],
                "Tone": {
                    "Valid": False,
                    "RefTone": -1,
                    "HypothesisTone": -1
                }
            }
        ],
        "SentenceId": -1,
        "RefTextId": -1,
        "KeyWordHits": None,
        "UnKeyWordHits": None
    },
    "final": 1
}

if __name__ == '__main__':
    result = extract_result(data)
    print(result)