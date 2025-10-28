import json

def compare_slang_files(file1_path, file2_path, output_path):

    with open(file1_path, 'r', encoding='utf-8') as f:
        data1 = json.load(f)
    
    with open(file2_path, 'r', encoding='utf-8') as f:
        data2 = json.load(f)
    

    dict1 = {item['informal_text']: item for item in data1}
    dict2 = {item['informal_text']: item for item in data2}
    
    result = []
    processed_informal = set()
    

    for informal, item1 in dict1.items():
        processed_informal.add(informal)
        
        if informal in dict2:

            item2 = dict2[informal]
            
            if item1['formal_text'] == item2['formal_text']:

                result.append(item1)
            else:

                merged_item = {
                    'informal_text': informal,
                    'formal_text': f"{item1['formal_text']}/{item2['formal_text']}",
                    'explanation': item1['explanation']
                }
                result.append(merged_item)
        else:

            result.append(item1)
    

    for informal, item2 in dict2.items():
        if informal not in processed_informal:
            result.append(item2)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Объединенный файл сохранен как: {output_path}")
    print(f"Всего записей в результате: {len(result)}")
    
    common_words = set(dict1.keys()) & set(dict2.keys())
    different_formal = 0
    
    for word in common_words:
        if dict1[word]['formal_text'] != dict2[word]['formal_text']:
            different_formal += 1
    
    print(f"Общих слов: {len(common_words)}")
    print(f"Слов с разными formal_text: {different_formal}")
    print(f"Уникальных слов в файле 1: {len(dict1) - len(common_words)}")
    print(f"Уникальных слов в файле 2: {len(dict2) - len(common_words)}")

def show_differences(file1_path, file2_path):

    with open(file1_path, 'r', encoding='utf-8') as f:
        data1 = json.load(f)
    
    with open(file2_path, 'r', encoding='utf-8') as f:
        data2 = json.load(f)
    
    dict1 = {item['informal_text']: item for item in data1}
    dict2 = {item['informal_text']: item for item in data2}
    
    common_words = set(dict1.keys()) & set(dict2.keys())
    
    print("\n=== СЛОВА С РАЗНЫМИ FORMAL_TEXT ===")
    for word in sorted(common_words):
        if dict1[word]['formal_text'] != dict2[word]['formal_text']:
            print(f"{word}: {dict1[word]['formal_text']} / {dict2[word]['formal_text']}")
    
    print("\n=== СЛОВА ТОЛЬКО В ПЕРВОМ ФАЙЛЕ ===")
    only_in_first = set(dict1.keys()) - set(dict2.keys())
    for word in sorted(only_in_first):
        print(f"{word}: {dict1[word]['formal_text']}")
    
    print("\n=== СЛОВА ТОЛЬКО ВО ВТОРОМ ФАЙЛЕ ===")
    only_in_second = set(dict2.keys()) - set(dict1.keys())
    for word in sorted(only_in_second):
        print(f"{word}: {dict2[word]['formal_text']}")

if __name__ == "__main__":
    file1 = "slangify_words.json"
    file2 = "a.json" 
    output = "slangify_words2.json"
    
    compare_slang_files(file1, file2, output)
    
    show_differences(file1, file2)