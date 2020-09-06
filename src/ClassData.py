from javalang.tree import ClassDeclaration, MethodDeclaration, FieldDeclaration, Literal, ElementValuePair

from src.FieldData import FieldData
from src.MethodData import MethodData


class ClassData:
    def __init__(self, data: ClassDeclaration):
        self.data = data
        self.name = data.name
        self. methods = {}
        self.is_feign_client = any(ann for ann in data.annotations if ann.name == "FeignClient")
        self.feign_name = None
        for ann in data.annotations:
            if ann.name == "FeignClient":
                for elt in ann.element:
                    if type(elt) == Literal:
                        self.feign_name = elt.value.replace('"', '').replace("'", '')
                    if type(elt) == ElementValuePair and elt.name == 'name':
                        self.feign_name = elt.value.value.replace('"', '').replace("'", '')

        for path, node in self.data.filter(MethodDeclaration):
            self. methods[node.name] = MethodData(node)

        self.fields = {}
        for path, node in self.data.filter(FieldDeclaration):
            field = FieldData(node)
            self.fields[field.name] = field
        self.autowired_fields = [field for field in self.fields.values() if field.isAutowired]
        self.feign_calls = {}
        self.is_rest_controller = any(method for method in self.methods.values() if method.mapping) or \
                                  any(ann for ann in self.data.annotations if ann.name == "RestController")
