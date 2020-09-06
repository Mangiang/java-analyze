from javalang.tree import FieldDeclaration


class FieldData:
    def __init__(self, data: FieldDeclaration):
        self.data = data
        self.type = data.type.name
        self.name = data.declarators[0].name
        self.isAutowired = any(ann for ann in data.annotations if ann.name == 'Autowired')