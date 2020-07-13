import json
import requests


# json_res = requests.get("http://127.0.0.1:5000/")
# json_dict = json_res.json()
# #print(json_dict)
# path_dict = json_dict.get("paths")
#
# component_dict = json_dict.get("components").get("schemas")
#print(json.dumps(component_dict))


def handle_component_dict(component_dict):
    param_dict = {}
    for k, v in component_dict.items():
        #print(k, v)
        param_list = []
        if v.get("required"):
            for param in v.get("required"):
                tm_dict = v.get("properties").get(param)
                tm_dict["required"] = True
                tm_dict["name"] = param
                tm_dict["in"] = "body"
                param_list.append(tm_dict)
            param_dict[k] = param_list
        else:
            print(11111)
            for k, v in v.get("properties").items():
                tm_dict = v
                tm_dict["required"] = False
                tm_dict["name"] = k
                tm_dict["in"] = "body"
                param_list.append(tm_dict)
            param_dict[k] = param_list
    print(param_dict)
    return param_dict


def run():
    json_res = requests.get("http://127.0.0.1:5000/api/")
    print(type(json_res.json()))
    json_dict = json_res.json()
    # print(json_dict)
    path_dict = json_dict.get("paths")

    component_dict = json_dict.get("components").get("schemas")

    param_dict = handle_component_dict(component_dict)

    #print(path_dict)

    for key, value in path_dict.items():
        # 每个接口的get post put delete
        for method, doc in value.items():
            # print(method, doc)
            # 如果有body
            component_list = []
            if doc.get("requestBody"):

                #print(doc.get("requestBody"))
                content = doc.get("requestBody").get("content")
                #print(content)

                for contentType in content.keys():
                    #print(content.get(contentType).get("schema"))
                    ref = content.get(contentType).get("schema").get("allOf")

                    if not ref:
                        #print(111111)
                        link = content.get(contentType).get("schema").get("$ref")
                        #print(link)
                        component_list.append(link.split("/")[-1])
                    else:
                        for i in ref:
                            #print(i)
                            component_list.append(i.get("$ref").split("/")[-1])
                    #print(component_list)
                des_list = []
                for component in component_list:
                    print(component, 1111)
                    tt = param_dict.get(component)
                    if tt:
                        des_list.extend(param_dict.get(component))

                if doc.get("parameters"):
                    #print(des_list)
                    path_dict[key][method].get('parameters').extend(des_list)
                else:
                    #print(des_list)
                    #print(path_dict[key][method])
                    if des_list:
                        path_dict[key][method]['parameters'] = des_list
                    #print(path_dict[key][method])
                del path_dict[key][method]['requestBody']
            # 如果没有body
            else:
                 #print(doc)
                pass

    #print(json.dumps(path_dict))

    json_dict["paths"] = path_dict
    return json.dumps(json_dict)


if __name__ == "__main__":

    run()
# with open("aaa.json", "w") as f:
#     f.write(json_dict.loads(json_dict))
