import requests


class Stack:
    """
    A class that implements the stack data structure
    
    Attributes:
        `stack` : A list that stores stack items
    
    Methods:
        `push(item)` : Adds an item to the top of the stack
        `pop()` : Removes and returns the top item from the stack if it is not empty
        `peek()` : Returns the top item from the stack without removing it if it is not empty
        `is_empty()` : Checks if the stack is empty
        `size()` : Returns the number of items in the stack
    """

    def __init__(self):
        """
        Initialize a new stack instance with an empty list
        """
        self.stack = []


    def push(self, item):
        """
        Adds an item to the top of the stack

        Args:
            item : Item to be added to the stack
        """
        self.stack.append(item)


    def pop(self):
        """
        Removes and returns the top item from the stack if it is not empty

        Returns:
            'Top item' if the stack is not empty
            Otherwise 'None'
        """
        if not self.is_empty():
            return self.stack.pop()
        else:
            return None


    def peek(self):
        """
        Returns the top item from the stack without removing it if it is not empty

        Returns:
            'Top item' if the stack is not empty
            Otherwise 'None'
        """
        if not self.is_empty():
            return self.stack[-1]
        else:
            return None


    def is_empty(self):
        """
        Checks if the stack is empty

        Returns:
            If the stack is empty 'True'
            Otherwise 'False'
        """
        return len(self.stack) == 0


    def size(self):
        """
        Returns the number of items in the stack

        Returns:
            Stack length (number of items)
        """
        return len(self.stack)
    


def remove_from_end(url, pop_str):
    """
    A function that removes a specific substring from the end of a URL string

    Args:
        url : URL containing the data to be fetched
        pop_str : Specific string to remove from the end of the URL string

    Returns:
        url : URL address with 'pop_str' removed from the end
    """
    if pop_str == 'skip':
        return url
    else:
        return url[:len(url) - len(pop_str)].rstrip()



def fetch_content(url):
    """
    A function to fetch JSON data from a given URL

    Args:
        url : URL from which JSON data is to be fetched

    Returns:
        JSON data

    Note:
        If an exception occurs, print an error message and return 'None'
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
        return None



def print_data(data):
    """
    A function to print the 'time' and 'name' values from the given dictionary

    Args:
        data : dictionary data
    
    Returns:
        time : 'time' within the dictionary data
        name : 'name' within the dictionary data

    Notes:
        Do not print if the 'time' key and 'name' key is not present.
    """
    print('time: ' + data['time'] + ' / name: ' + data['name'])



def show_table(url):
    """
    A function to print the list of tables from the given URL and update the URL

    Args:
        url : URL from which JSON data is to be fetched
    
    input:
        'table number' or 'exit'

    Returns:
        When 'exit' is entered, 'None'
        When 'table number' is entered, 'the updated URL'
    """
    table_json = fetch_content(url)
    print('-----Table List-----')
    for i, table in enumerate(table_json['data_table_list'], 1):
        print(str(i) + ': ' + table)
    table_input = input("Enter the table number / exit: ")
    if table_input == 'exit':
        return None
    else:
        table_url = '=' + table_json['data_table_list'][int(table_input) - 1]
        url = url + table_url
        url_stack.push(table_url)
        table_data = table_url.split('=')[-1]
        data_stack.push({'table': table_data})
        return url



def show_data_id(url):
    """
    A function to print the list of data IDs from the given URL and update the URL

    Args:
        url : URL from which JSON data is to be fetched
        
    input:
        'data id number' or 'exit' or 'undo'

    Returns:
        When 'exit' is entered, 'None'
        When 'undo' is entered, 'previous URL'
        When 'data id number' is entered, 'the updated URL'
    """
    data_id_json = fetch_content(url)
    print('-----Data ID List-----')
    for i, data_id in enumerate(data_id_json['data_ids_list'], 1):
        print(str(i) + ': ' + data_id)
    data_id_input = input("Enter the data id number / exit / undo: ")
    if data_id_input == 'exit':
        return None
    elif data_id_input == 'undo':
        url = remove_from_end(url, url_stack.pop())
        data_stack.pop()
        return url
    else:
        data_id_url = '&data_id=' + data_id_json['data_ids_list'][int(data_id_input) - 1]
        url = url + data_id_url
        url_stack.push(data_id_url)
        data_id_data = data_id_url.split('=')[-1]
        data_stack.push({'data_id': data_id_data})
        return url



def show_start_time(url):
    """
    A function to print the start time from the given URL and update the URL

    Args:
        url : URL from which JSON data is to be fetched

    input:
        'start time (YYYY-MM-DD)' or 'exit' or 'undo'
        
    Returns:
        When 'exit' is entered, 'None'
        When 'undo' is entered, 'previous URL'
        When 'start time (YYYY-MM-DD)' is entered, 'the updated URL'
    """
    start_time_json = fetch_content(url)
    print('-----Data Info-----')
    for key in start_time_json.keys():
        if start_time_json[key] == '':
            start_time_json[key] = 'None'
        print(key + ': ' + start_time_json[key])
    start_time_input = input("Enter the start time (YYYY-MM-DD) / exit / undo: ")
    if start_time_input == 'exit':
        return None
    elif start_time_input == 'undo':
        url = remove_from_end(url, url_stack.pop())
        data_stack.pop()
        return url
    else:
        start_time_url = '&start_time=' + start_time_input
        url = url + start_time_url
        url_stack.push(start_time_url)
        data_stack.push({'start_time': start_time_input})
        return url



def show_data_list(url):
    """
    A function to print the list of data from the given URL, update the URL, and download the file

    Args:
        url : URL from which JSON data is to be fetched

    input:
        'end time (YYYY-MM-DD)' or 'download' or 'skip' or 'exit' or 'undo'
        
    Returns:
        When 'exit' is entered, 'None'
        When 'undo' is entered, 'previous URL'
        When 'skip' is entered, 'updated URL'
        When 'end time (YYYY-MM-DD)' is entered, 'updated URL'
    """
    data_list_json = fetch_content(url)
    print('-----Data List-----')
    for key in data_list_json.keys():
        if key != 'data_list':
            print(key + ': ' + data_list_json[key])
        else:
            print(key + ': ')
            data_list = data_list_json[key]
            for data in data_list:
                print_data(data)

    data_key = list(data_stack.peek().keys())[0]
    if data_key != 'end_time':
        end_time_input = input("Enter the end time (YYYY-MM-DD) / skip / exit / undo: ")
    else:
        end_time_input = input("Enter the exit / undo: ")
    if end_time_input == 'exit':
        return None
    elif end_time_input == 'undo':
        url = remove_from_end(url, url_stack.pop())
        data_stack.pop()
        return url
    elif end_time_input == 'skip':
        url_stack.push('skip')
        data_stack.push({'end_time': None})
        return url
    else:
        end_time_url = '&end_time=' + end_time_input
        url = url + end_time_url
        url_stack.push(end_time_url)
        data_stack.push({'end_time': end_time_input})
        return url


data_stack = Stack()
url_stack = Stack()



def data_info():
    """
    A function that allows users to interact and search for data
    """
    global data_stack, url_stack
    url = 'http://swds.kasi.re.kr/swpipeline/api/search.php?table'
    while True:
        print()
        if data_stack.is_empty():
            url = show_table(url)
            if url == None:
                break
        else:
            data_key = list(data_stack.peek().keys())[0]
            if data_key == 'table':
                url = show_data_id(url)
                if url == None:
                    break
            elif data_key == 'data_id':
                url = show_start_time(url)
                if url == None:
                    break
            elif data_key == 'start_time' or data_key == 'end_time':
                url = show_data_list(url)
                if url == None:
                    break

    data_stack = Stack()
    url_stack = Stack()
    
class Downloader:
    """
    A class that downloads and outputs data
    """
    def __init__(self, data_list_json, url):
        """
        Initialize an instance of the Downloader class

        Args:
            data_list_json : JSON data containing a list of data to download
            url : URL from which JSON data is to be fetched 
        """
        self.data_list_json = data_list_json
        self.url = url

    def print_data(self):
        """
        A function to print the list of data

        Returns:
            'data_list', Key-value pairs
        """
        for key, value in self.data_list_json.items():
            if key != 'data_list':
                print(f"{key}: {value}")
            else:
                print(f"{key}:")
                data_list = value
                for data in data_list:
                    time = data.get('time')
                    name = data.get('name')
                    print(f"time: {time} / name: {name}")

    def download(self, file_path):
        """
        A function to download data

        Args:
            file_path : The path to download the file

        Exceptions:
            Raising an exception when the JSON data is invalid or when the key 'data_list' is missing
        """
        json_data = fetch_content(self.url)
        url = self.url.replace('search', 'download')

        if not json_data or 'data_list' not in json_data:
            raise Exception("Invalid JSON data or missing 'data_list' key.")
        
        if len(json_data['data_list']) == 1:
            if file_path == 'skip':
                file_path = json_data['data_list'][0]['name']
        else:
            if file_path == 'skip':
                url_data_line = url.split('?')[-1]
                url_data_list = url_data_line.split('&')
                url_dict = {}
                for url_data in url_data_list:
                    key, value = url_data.split('=')
                    url_dict[key] = value
                file_path = url_dict['table'] + '_' + url_dict['data_id'] + '_' + json_data['data_start_time'] + '_' + json_data['data_end_time'] + '.zip'

        with open(file_path, 'wb') as file:
            file.write(requests.get(url).content)
        print("\nDownload completed")
        url = url.replace('download', 'search')


def search(table_name, data_id, start_time, end_time=None):
    """
    A function that searches for specific data, prints the data, and returns a Downloader object

    Args:
        table_name : The table name you want to fetch
        data_id : The data ID you want to fetch
        start_time : The start time of the data you want to fetch
        end_time : The end time of the data you want to fetch (optional)

    Returns:
        Downloader : A Downloader object that includes the searched data
    """
    url = f'http://swds.kasi.re.kr/swpipeline/api/search.php?table={table_name}&data_id={data_id}&start_time={start_time}'
    if end_time is not None:
        url = f'{url}&end_time={end_time}'

    data_list_json = fetch_content(url)

    for key, value in data_list_json.items():
        if key != 'data_list':
            print(f"{key}: {value}")
        else:
            print(f"{key}:")
            data_list = value
            for data in data_list:
                time = data.get('time')
                name = data.get('name')
                print(f"time: {time} / name: {name}")

    return Downloader(data_list_json, url)