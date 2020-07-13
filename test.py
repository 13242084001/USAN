import sys
from urllib.parse import urlparse
from coreapi import Client
import yaml
import os
import pathlib
import re
import codecs


def generate_tavern_yaml(json_path):
    client = Client()
    #print(client.__dict__)
    d = client.get(json_path, format="openapi")
    #print(d)
    #print(d.data)

    output_yaml(d.links)
    for routes in d.data.keys():
        #print(os.getcwd())
        #print(routes)
        test_dir = routes.split()[-1]
        os.mkdir(test_dir) if not os.path.isdir(test_dir) else ...
        pathlib.Path(test_dir + "/" + "__init__.py").touch()
        output_yaml(d.data[routes], test_dir)


def output_yaml(links, test_dir=""):
    #print(prefix, 111111)
    test_dict = {}
    p = re.compile('<[^>]+>')
    for test_name in links.keys():
        #print(links[test_name], "ffffff")
        # default_name = get_name(
        #     prefix, test_name, links[test_name].action, links[test_name].url
        # )
        description = links[test_name].description
        if description:
            description = p.sub("", links[test_name].description.split()[-1])
            description = "".join(re.findall(r'[^\*"/:?\\|<>，。]', description, re.S))  # 注意，这里有中文字符
            default_name = links[test_name].title.replace(" ", "") + "-" + description
        else:
            default_name = links[test_name].title.replace(" ", "")
        name = links[test_name].description.split()[-1] if links[test_name].description else str("---")
        test_dict["test_name"] = default_name
        #print(default_name)
        request = {
            "url": links[test_name].url,
            "method": str.upper(links[test_name].action),
        }
        """
        if links[test_name].encoding:
            print(links[test_name].encoding)
            request["headers"] = {"content-type": links[test_name].encoding}
        """

        headers, fileds = get_request(links[test_name].fields)
        if headers:
            request["headers"] = headers
        if fileds.get("json"):
            request["json"] = fileds.get("json")
        if fileds.get("params"):
            request["params"] = fileds.get("params")

        response = {"strict": False, "status_code": 200}
        inner_dict = {"name": name, "request": request, "response": response}

        test_dict["stages"] = [inner_dict]
        #print(test_dict)
        with open(test_dir + "/" + "test_{0}.tavern.yaml".format(description.replace("-", "_")), "w") as f:
            des_str = yaml.dump(test_dict, explicit_start=True, default_flow_style=False, allow_unicode=True)
            #print(type(des_str))
            #des_str = des_str.encode("gbk")
            f.write(des_str)



def get_request(fields):
    header_dict = {}
    field_dict = {"json": {}, "params": {}}
    #print(fields)
    for field in fields:
        # print(field)
        if field.location == "header":
            header_dict[field.name] = "required" if field.required else "optional"
        elif field.location == "body":
            #print(field)
            field_dict["json"][field.name] = "required" if field.required else "optional"
            #print(field_dict)
        elif field.location == "query":
            field_dict["params"][field.name] = "required" if field.required else "optional"
    return header_dict, field_dict


def get_request_placeholders(fields):
    field_dict = {}
    #print(fields)
    for field in fields:
        #if field.location == "body":
        field_dict[field.name] = "required" if field.required else "optional"
    print(field_dict)
    return field_dict


def get_name(prefix, test_name, action, url):
    name = f"{action} "

    if prefix and test_name:
        name += f"{prefix}/{test_name}"
    elif test_name:
        name += test_name
    elif prefix:
        name += f"{prefix} " + urlparse(url).path
    else:
        name += urlparse(url).path
    #print(name)
    return name


def display_help():
    print("pub_tavern.py <url to openapi.json>")
    print(
        "eg: pub_tavern.py https://raw.gles/v2.0/json/petstore-simple.json"
    )
    exit(-1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        display_help()
    generate_tavern_yaml(sys.argv[1])

