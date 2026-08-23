import re, html, sys, os

def extract(dom_path):
    t = open(dom_path, 'r', encoding='utf-8').read()
    result = {}

    m = re.search(r'<title>([^<]+)</title>', t)
    result['title'] = m.group(1).replace(' | EZ.Encoder Academy', '') if m else ''

    m = re.search(r'class="text-sm font-semibold[^"]*">([^<]+)</span>', t)
    result['attachment_name'] = m.group(1) if m else ''

    m = re.search(r'class="text-xs font-regular[^"]*">([^<]+)</span>', t)
    result['attachment_size'] = m.group(1) if m else ''

    fi = t.find('file-wrapper')
    m = re.search(r'href="(https://assets-v2\.circle\.so/[^"]+)"', t[fi:]) if fi >= 0 else None
    result['attachment_url'] = m.group(1) if m else ''

    i = t.find('file-wrapper')
    j = t.find('<ol>', i) if i >= 0 else -1
    if j >= 0:
        seg = t[j:j+40000]
        seg = re.sub(r'<ol>', '\n', seg)
        seg = re.sub(r'</ol>', '\n', seg)
        seg = re.sub(r'<li>', '\n* ', seg)
        seg = re.sub(r'</li>', '', seg)
        seg = re.sub(r'</?p[^>]*>', '', seg)
        seg = re.sub(r'<a[^>]*href="([^"]+)"[^>]*>.*?</a>', lambda m: m.group(1), seg)
        seg = re.sub(r'<[^>]+>', '', seg)
        seg = html.unescape(seg)
        seg = re.sub(r'\n{3,}', '\n\n', seg)
        for marker in ('See more', 'See More'):
            k = seg.find(marker)
            if k >= 0:
                seg = seg[:k]
        result['body'] = seg.strip()
    else:
        result['body'] = ''

    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python extract_post.py <rendered_dom.txt> [out.txt]')
        sys.exit(1)
    dom = sys.argv[1]
    res = extract(dom)
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(dom), 'extracted.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('TITLE: %s\n' % res['title'])
        f.write('ATTACHMENT_NAME: %s\n' % res['attachment_name'])
        f.write('ATTACHMENT_SIZE: %s\n' % res['attachment_size'])
        f.write('ATTACHMENT_URL: %s\n' % res['attachment_url'])
        f.write('\nBODY:\n%s\n' % res['body'])
    print('written:', out)
