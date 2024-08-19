

class Header(dict):

    def __init__(self):
        self.header = {}

    def __repr__(self):
        return f"Header(header={self.header})"

    def __str__(self):
        return f"Header(header={self.header})"

    def __getitem__(self, key):
        return self.header[key]
    
    def __setitem__(self, key, value):
        self.header[key] = value

    def __delitem__(self, key):
        del self.header[key]

    def __iter__(self):
        return iter(self.header)
    
    def __len__(self):
        return len(self.header)
    
    def __contains__(self, key):
        return key in self.header
    
    def keys(self):
        return self.header.keys()
    
    def values(self):
        return self.header.values()
    
    def items(self):
        return self.header.items()
    
    def get(self, key):
        return self.header[key]
    
    def set(self, key, value):
        self.header[key] = value

    def delete(self, key):
        del self.header[key]

    def delete_all(self):
        self.header.clear()

    def delete_all_except(self, key):
        keys = self.keys()
        for k in keys:
            if k != key:
                del self.header[k]

    def delete_all_except_these(self, keys):
        keys = self.keys()
        for k in keys:
            if k not in keys:
                del self.header[k]

    
def fits_header_to_Header(fits_header):
    header = Header()
    keycomments = {}
    for card in fits_header.cards:
        card.verify("fix") 
        key = card.keyword
        comment = card.comment
        value = card.value
        if(key == ""):
            continue
        header[key] = value
        if(comment != ""):
            keycomments[key] = comment
    header["KEYCOMMENTS"] = keycomments
    return header
    