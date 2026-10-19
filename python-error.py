
def get_value(dict, key):
    if key in dict:
        return dict.gey(key)
    else:
        return None


my_dict = {'key1': "example"}
try:
    value = get_value(my_dict, 'key1')
    if value is None:
        print("Key missing")
except KeyError:
    print("Key missing")
