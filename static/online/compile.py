import subprocess
import sys
import os
import wand.image
import re
import math
import json

def compile(entry):
    entry_file = os.path.basename(entry)
    entry_directory = os.path.dirname(entry)
    directory = '/tmp'
    retcode = subprocess.Popen(['pdflatex', '-interaction=nonstopmode', '-8bit', '-output-directory={}'.format(os.path.abspath(directory)), '-jobname=output', entry_file], stdout=None, stderr=None, cwd=entry_directory).wait()
    if retcode!=0:
        raise subprocess.CalledProcessError(retcode, 'pdflatex')
    with open(os.path.join(directory, 'output.aux')) as f:
        aux = f.read()
    points = [(x, float(y)) for (x, y) in re.findall(r'\\zref\@newlabel\{([^\}]+)\}\{\\posy\{(\d+)\}\}', aux)]
    image = wand.image.Image(resolution=100, filename=os.path.join(directory, 'output.pdf'))
    y0 = points[0][1]
    y1 = points[-1][1]
    points = [(x, int(math.ceil((image.size[1])*float(y0-y)/float(y0-y1)))) for x, y in points]
    config = [x[len('config='):] for x, _ in points if x.startswith('config=')]
    config = dict([(x.split('=')[0], '='.join(x.split('=')[1:])) for x in config])
    points = [(x, y) for x, y in points if not x.startswith('config=')]
    dname = entry_file
    if dname.rindex('.')!=-1:
        dname = dname[:dname.rindex('.')]
    dname = 'sets/{}'.format(dname)
    obj = {}
    os.system("rm -rf {}".format(dname))
    os.system("mkdir -p {}".format(dname))
    obj['name'] = config.get('name', entry_file)
    obj['contents'] = []
    points = [(x, y0, y1) for ((x, y0), (_, y1)) in zip(points[:-1], points[1:])]
    part = {}
    def push():
        if part.get('type') is not None:
            obj['contents'].append(part.copy())
        part.clear()
        part['imgs'] = []
    push()
    all_imgs = []
    for x, y0, y1 in points:
        def append(is_hint=False):
            if y1!=y0:
                all_imgs.append('{}/{}.png'.format(dname, len(all_imgs)))
                img = image[:, y0:y1]
                img.format='png'
                img.save(filename=all_imgs[-1])
                if is_hint:
                    part['hint'] = all_imgs[-1]
                else:
                    part['imgs'].append(all_imgs[-1])
        def hint():
            append(True)
        if x=='begin_document':
            push()
            part['type']='static'
            append()
        elif x=='begin_choices':
            push()
            part['type']='single'
            hint()
        elif x=='begin_multi':
            push()
            part['type']='multi'
            part['answer'] = []
            hint()
        elif x=='begin_freeform':
            push()
            part['type']='freeform'
            append()
        elif x in ['end_choices', 'end_multi', 'end_freeform']:
            push()
            part['type']='static'
            append()
        elif x.startswith('ans_equals@'):
            append()
            part['answer'] = x[len('ans_equals@'):]
        elif x=='true_choice':
            if part['type']=='single':
                part['answer']=len(part['imgs'])
            elif part['type']=='multi':
                part['answer'].append(len(part['imgs']))
            append()
        elif x=='false_choice':
            append()
        elif x=='hint':
            hint()
    push()
    with open(os.path.join(dname, 'meta.js'), 'w') as f:
        f.write('sets.push({})'.format(json.dumps(obj)))

if __name__ == '__main__':
    for s in os.listdir('latex/sets'):
        try:
            int(s)
            path = os.path.abspath(os.path.join('latex/sets', s, 'set{}.tex'.format(s)))
            compile(path)
        except ValueError:
            pass
