from datasets import Dataset, load_from_disk, load_dataset
import re


def getAndSaveDatasetDict(path1, path2, dataDict = None):
    """
        get dataset from name 'path1',
        save dataset to disk 'path2'
        ---
        return Dataset Dictionary
    """
    if dataDict is None:
        dataDict = load_dataset(path1)
    dataDict.save_to_disk(path2)
    

def loadDatasetDisk(path):
    """
        loads dataset dictionary from disk path
    """
    return load_from_disk(path)
    
    
def saveDatasetDisk(dataset, path):
    """
        saves dataset dictionary to disk path
    """
    dataset.save_to_disk(path)


def prepareData(dataset, poetCount=5, poemCount=100, poemMinLength=128, poemMaxLength=1024, cols=['poem', 'poet']):
    """
        Prepare the dataset dictionary according to given parameters and return it.
    """
    if dataset is None:
        print("Dataset is None")
        return None

    dataset = dataset.copy()

    for col in dataset['train'].column_names:
        if col not in cols:
            print(f'{col} will be deleted from dataset')
            dataset['train'] = dataset['train'].remove_columns(col)
        else:
            print(f'{col} is being kept')
    
    tmp_data = {}
    selected_poets = 0
    data = []

    for example in dataset['train']:
        poet = example['poet']
        poem = example['poem']
        
        if len(poem) < poemMinLength or len(poem) > poemMaxLength:
            continue
        
        if poet not in tmp_data:
            tmp_data[poet] = []

        tmp_data[poet].append(poem)

    for poet, poems in tmp_data.items():
        if len(poems) >= poemCount:
            for poem in poems[:poemCount]:
                data.append({'poet': poet, 'poem': poem})
            selected_poets += 1
            if selected_poets == poetCount:
                break

    return Dataset.from_dict({'train' : {'poet': [item['poet'] for item in data],
                                        'poem': [item['poem'] for item in data]}})

    
def cleaning(text):
    """
        clean the given text and return it
    """
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r' +', ' ', text)
    return text
    

def cleanData(dataset, col = 'poem'):
    """
        clean the given dataset
    """
    for data in dataset:
        data[col] = cleaning(data[col])
    
    return dataset


if __name__ == "__main__":
    """
        operations
    """
    ds_name = "beratcmn/instruction-turkish-poems"
    dir_path1 = "turkish_poems"
    dir_path2 = "turkish_poems_cleaned"
    
    getAndSaveDatasetDict(ds_name, dir_path1)
    datasetDict = loadDatasetDisk(dir_path1)
    datasetPrepared = prepareData(datasetDict)
    print(datasetPrepared)
    datasetCleaned = cleanData(datasetPrepared)
    saveDatasetDisk(datasetCleaned, dir_path2)