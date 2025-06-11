import yaml
import json
import base64
import os


def normalize_resources(resources):
    for r in resources:
        normalize_resource(r)

# 补充颜色,layout,uuid,children,id,_importDepth


def normalize_resource(r):
    r['subtitle'] = r['subtitle'] if 'subtitle' in r.keys() else ""
    r['description'] = r['description'] if 'description' in r.keys() else ""
    r['backgroundColor'] = r['backgroundColor'] if 'backgroundColor' in r.keys() else "white"
    r['style'] = r['style'] if 'style' in r.keys() else "default"
    r['iconStyle'] = r['iconStyle'] if 'iconStyle' in r.keys() else "default"
    r['layout'] = r['layout'] if 'layout' in r.keys() else {'compactness': 1, 'sizes': 'auto'}
    r['id'] = r['id'] if 'id' in r.keys() else r['name']
    r['uuid'] = r['id']
    r['_importDepth'] = None  # 有时是0 ?
    r['children'] = r['children'] if 'children' in r.keys() else []
    r['color'] = r['color'] if 'color' in r.keys() else 'navy'  # navy default?
    # 处理 import AWS 的情况
    for child in r['children']:
        normalize_resource(child)


def normalize_perspectives(perspectives):
    for p in perspectives:
        if 'relations' in p.keys():
            for r in p['relations']:
                r['from'] = [x.strip() for x in r['from'].split(',')]
                r['to'] = [x.strip() for x in r['to'].split(',')]
                r['namespace'] = ""
        elif 'sequence' in p.keys():
            p['sequence']['namespace'] = ""
        p['id'] = p['name']
        p['_importDepth'] = 0


imgs = {}
begin = 'url('
headers = {
    'svg': 'data:image/svg+xml;base64,',
    'png': 'data:image/png;base64,',
    'jpg': 'data:image/jpeg;base64,',
    'jpeg':  'data:image/jpeg;base64,',
}
end = ')'


def inline_image(img: str):
    # find img from official ilograph icon lib
    try:
        with open('icons/'+img, 'br') as i:
            format = img.split('.')[-1]
            file = i.read()
            body = base64.b64encode(file).decode('ascii')
            imgs[img] = begin + headers[format] + body + end
    except FileNotFoundError:
        print('img not found', img)
        pass
    # find img from local path
    pass

    return None


def inline_all_images(d: dict):
    if isinstance(d, list):
        for i in d:
            inline_all_images(i)
        return
    elif isinstance(d, dict):
        if 'icon' in d.keys():
            inline_image(d['icon'])
        if 'children' in d.keys():
            inline_all_images(d['children'])


def render(d, imgs, output_filename):
    with open('template.html', 'r') as f:
        template = str(f.read())

        d_json = str(json.dumps(d))
        d_json = d_json.replace('\\', '\\\\')
        d_json = d_json.replace('"', '\\"')
        template = template.replace('placeholder_json', d_json)
        template = template.replace('placeholder_icons', json.dumps(imgs))

        with open('debug.json', 'w') as f:
            f.write(json.dumps(d, indent=4))
        with open('debug-icon.json', 'w') as f:
            f.write(json.dumps(imgs, indent=4))
        with open(output_filename, 'w') as f:
            f.write(template)


def main():
    with open('simple.yaml', 'r') as file:
        d = yaml.safe_load(file)
        
    normalize_resources(d['resources'])
    normalize_perspectives(d['perspectives'])
    inline_all_images(d['resources'])
    
    
    base_name = os.path.splitext(os.path.basename(yaml_file))[0]
    output_file = f"{base_name}.html"
    render(d, imgs, output_file)



if __name__ == "__main__":
    main()
