from javalang.tree import ClassDeclaration, MethodDeclaration, Literal, ElementValuePair

from src.MethodData import MethodData


class InterfaceData:
    def __init__(self, data: ClassDeclaration):
        self.data = data
        self.name = data.name
        self.is_feign_client = any(ann for ann in data.annotations if ann.name == "FeignClient")
        self.mappings = []
        self.methods = {}
        self.feign_name = None
        for ann in data.annotations:
            if ann.name == "FeignClient":
                for elt in ann.element:
                    if type(elt) == tuple:
                        val = elt[1]
                        if type(val) == Literal:
                            self.feign_name = val.value.replace('"', '').replace("'", '')
                    elif type(elt) == Literal:
                        self.feign_name = elt.value.replace('"', '').replace("'", '')
                    elif type(elt) == ElementValuePair and elt.name == 'name':
                        self.feign_name = elt.value.value.replace('"', '').replace("'", '')
        for path, node in self.data.filter(MethodDeclaration):
            self.methods[node.name] = MethodData(node)
            for annotation in node.annotations:
                if annotation.name == "RequestMapping":
                    self.mappings.append(node)
