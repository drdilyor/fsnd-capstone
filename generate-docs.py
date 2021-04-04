#!/usr/bin/env python3
"""
Copyright 2021 Dilyorbek Valijonov (drdilyor).

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import json
import re

from models import Movie, Actor

__authors__ = ['drdilyor@outlook.com']

re_route = re.compile(r"@app\.route\('(?P<endpoint>[-/<>:\w]+)'(, methods=\['(?P<method>\w+)'])?\)")
re_perm = re.compile(r"@requires_auth\('([\w:]+)'\)")
re_def_name = re.compile(r"def (\w+)\(")
re_abort = re.compile(r"abort\((\d+)\)")

re_error_handler = re.compile(r"@app.errorhandler\((\d+)\)")
re_py_docs = re.compile(r'"""(.*?)"""', re.DOTALL)
re_error_return = re.compile(r"return (.*?}), \d+", re.DOTALL)

def snake_to_readable(n):
    return ' '.join(i.capitalize() if len(i) > 1 else i for i in n.split('_'))


class Route:
    host = "http://localhost:5000"

    def __init__(self, code):
        match = re_route.search(code)
        self.endpoint = match.group('endpoint')
        self.method = match.group('method') or 'GET'
        match = re_perm.search(code)
        if match:
            self.perm = match.group(1)
        else:
            self.perm = None
        match = re_def_name.search(code)
        self.name = match.group(1)
        if 'movie' in self.name:
            self.model = Movie
        elif 'actor' in self.name:
            self.model = Actor
        else:
            self.model = None
        self.response_is_list = '<int:pk>' not in self.endpoint and self.method == 'GET'
        self.raises = set(re_abort.findall(code))

    @property
    def example_endpoint(self):
        return self.endpoint.replace('<int:pk>', '1')

    def example_content(self):
        return self.model.example_in()

    def example_response(self):
        if self.model is None:
            return
        res = self.model.example_out()
        key = self.model.__name__.lower()
        if self.response_is_list:
            res = [res]
            key = key + 's'
        return {
            'success': True,
            key: res,
        }

    def curl(self):
        res = [f'curl {self.host}{self.example_endpoint}']
        if self.method != 'GET':
            res.append(f'-X {self.method}')
        if self.perm:
            res.append('-H "Authorization: Bearer $token"')
        if self.method in ['POST', 'PATCH', 'PUT']:  # though there are no put endpoints
            res.append("-H 'Content-Type: application/json'")
            if self.model:
                res.append(f"-d '{json.dumps(self.example_content())}'")
            else:
                res.append(f"-d '!No example available!'")
        return ' \\\n'.join(res)

    def generate(self):
        res = (
            f"### {snake_to_readable(self.name)}\n"
            f"#### Endpoint\n"
            f"`{self.method} {self.endpoint}`\n"
            f"\n"
            f"#### Sample request\n"
            f"```shell script\n{self.curl()}\n"
            f"```\n\n"
            "The above command returns json structured like this:\n"
            f"```json\n{json.dumps(self.example_response() or 'No example response available', indent=2)}\n"
            f"```\n"
            f"\n"
            f"#### Permission\n"
            f"`{self.perm or 'This endpoint is publicly available'}`"
            f"\n"
            f"#### Raises\n"
            + ('\n'.join(
                f"- **[{e}](#{e})**" for e in self.raises
            ) or "This endpoint doesn't raise any errors\n")
        )
        return res


class ErrorHandler:
    def __init__(self, code):
        self.error_code = re_error_handler.search(code).group(1)
        self.name = re_def_name.search(code).group(1)
        self.docs = re_py_docs.search(code).group(1)
        self.return_dict = eval(re_error_return.search(code).group(1))

    def generate(self):
        res = (
            f"### {self.error_code}\n"
            f"{snake_to_readable(self.name)}: {self.docs}\n"
            f"\n"
            f"#### Response be like\n"
            f"```json\n{json.dumps(self.return_dict, indent=2)}\n"
            f"```\n"
        )
        return res


class DocsGenerator:
    file = 'src/app.py'
    pre_file = 'docs-pre.md'
    post_file = 'docs-post.md'
    dont_edit = """> **Warning**: auto generated, do NOT edit it by hand! Instead make changes to docs-pre.md and docs-post.md files\n\n"""  # noqa

    def __init__(self):
        self.code = open(self.file).read()
        blocks = re.split('\n{2,}', self.code)
        self.routes = []
        self.errors = []
        for b in blocks:
            # If first line of "block" is an @app.route(...)
            if re_route.search(b.partition('\n')[0]) is not None:
                self.routes.append(Route(b))
        for b in blocks:
            # Error handlers
            if re_error_handler.search(b) is not None:
                self.errors.append(ErrorHandler(b))

    def generate(self):
        return (
            self.dont_edit +
            f"{open(self.pre_file).read()}\n"
            "## API Docs\n\n"
            + '\n'.join(r.generate() for r in self.routes) +
            "\n\n## API Errors\n\n"
            + '\n'.join(e.generate() for e in self.errors)
        )


if __name__ == '__main__':
    # print(DocsGenerator().generate())
    print(DocsGenerator().generate())

