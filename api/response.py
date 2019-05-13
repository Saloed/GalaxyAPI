import dicttoxml

from django.http import JsonResponse, HttpResponse


class XmlResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        kwargs.setdefault('content_type', 'application/xml')
        super().__init__(content=data, **kwargs)


def json_response(data):
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False})


class XMLNamedNode:
    def __init__(self, node, name):
        self.node = node
        self.name = name

    def __len__(self):
        return len(self.node)


def _make_xml_item_selector(parent_to_name):
    def select_name(parent):
        return parent_to_name.get(parent, 'item')

    return select_name


def _recollect_named_nodes(root, parent_name, parent_to_name: dict):
    if isinstance(root, XMLNamedNode):
        current_name = parent_to_name.get(parent_name, None)
        if current_name is None:
            parent_to_name[parent_name] = root.name
        elif current_name != root.name:
            raise ValueError("Duplicate parents found in XML")
        return _recollect_named_nodes(root.node, parent_name, parent_to_name)
    elif isinstance(root, dict):
        return {
            key: _recollect_named_nodes(value, key, parent_to_name)
            for key, value in root.items()
        }
    elif isinstance(root, (list, tuple)):
        return [
            _recollect_named_nodes(it, parent_name, parent_to_name)
            for it in root
        ]
    else:
        return root


def xml_response(data):
    parent_to_name = {}
    data_without_named_nodes = _recollect_named_nodes(data, None, parent_to_name)
    name_selector = _make_xml_item_selector(parent_to_name)
    xml_data = dicttoxml.dicttoxml(data_without_named_nodes, attr_type=False, item_func=name_selector)
    return XmlResponse(xml_data)
