import os, re
from os import path

CWD = path.dirname(os.path.realpath(__file__))
SRC_DIR = "src"
ROUTES_PATH = "routes"
BUILD_FILE_NAME = "build"
VALID_METHODS = ["get", "post", "options", "patch", "delete", "any", "put", "head"]

MODULE_NAME = path.join(open("go.mod").readline().split(" ")[1], SRC_DIR).replace("\n", "").replace("\\", "/")

def getFiles(file: str = "", basepath = ROUTES_PATH):
    if file.endswith(".go"):
        return file.lower().replace(".go", "")

    folderPath = path.join(CWD, SRC_DIR, basepath, file)
    files = [getFiles(f, folderPath) for f in os.listdir(folderPath)]

    if len(file) > 0:
        return {file: files}
    else:
        return files


def getImports(groups, cpath = ROUTES_PATH, r = False):
    imports = []

    pathAdded = False

    if type(groups) == dict:
        for key in groups.keys():
            imports = [
                *imports,
                *getImports(
                    groups[key], path.join(cpath, key).replace("\\", "/"), True
                ),
            ]

    for group in groups:
        if type(group) == str and not pathAdded and cpath != ROUTES_PATH:
            importPath = path.join(cpath).replace("\\", "/")
            imports.append(
                f'{re.sub(r"[/]", "_", re.sub(r"-", "", importPath))} "{MODULE_NAME}/{importPath}"'
            )
            pathAdded = True
        elif type(group) == dict:
            for key in group.keys():
                imports = [
                    *imports,
                    *getImports(
                        group[key], path.join(cpath, key).replace("\\", "/"), True
                    ),
                ]

    if not r:
        imports.append('"github.com/gin-gonic/gin"')

    return imports


def joiner(fc: list):
    indent = 0
    string = ""

    for line in fc:
        if re.match(r"^[\])}].*", line):
            indent -= 1
        string = string + ("\t" * indent) + line + "\n"
        if re.match(r".*[({[]$", line):
            indent += 1

    return string


def createRouter(routeList: list, initalPath="/", parentVariable="r", n = False):
    routerLines = []

    if not n:
        routerLines = ["func CreateRouter(r *gin.Engine) {"]

    for route in routeList:
        # If there is a sub route
        if type(route) == dict:
            for subroute in route.keys():
                if len(route[subroute]) == 0:
                    continue
                spv = f'{parentVariable}_{re.sub(r"-", "", subroute)}'  # sub path parent variable
                spv = re.sub(r"/", "_", spv)
                if subroute == "middleware":
                    middlewareList = []
                    importVar = re.sub(
                        r"[/]",
                        "_",
                        f"{ROUTES_PATH}{re.sub(r'-', '', initalPath)}middleware",
                    )

                    for middleware in route["middleware"]:
                        middlewareList.append(f"{importVar}.{str(middleware).upper()}")
                    routerLines.append(
                        f'{parentVariable}.Use({", ".join(middlewareList)})'
                    )
                    continue

                sp = "/" + path.basename(subroute)  # sub path path
                routev = sp

                if re.match(r"__.*__", subroute):
                    routev = f"/:{str(path.basename(subroute)).replace('__', '')}"

                routerLines.append(
                    f'{spv} := {parentVariable}.Group("{routev}"); ' + "{"
                )
                routerLines += createRouter(route[subroute], path.join(initalPath, subroute).replace("\\", "/"), spv, True)
                routerLines.append("}")
        elif type(route) == str:
            routeMethod = route.replace(".go", "").upper()

            importVar = ""
            if n:
                importVar = re.sub(
                    r"[/]", "_", f"{ROUTES_PATH}{re.sub(r'-', '', initalPath)}."
                )

            if routeMethod == "MIDDLEWARE":
                routerLines.append(f"{parentVariable}.Use({importVar}MIDDLEWARE)")
                continue

            if routeMethod.lower() not in VALID_METHODS:
                print(
                    f"'{routeMethod}' is not a method (found at {ROUTES_PATH}{initalPath})"
                )
                continue
            if routeMethod == "ANY":
                routeMethod = "Any"

            routerLines.append(
                f'{parentVariable}.{routeMethod}("/", {importVar}{routeMethod.upper()})'
            )
        else:
            print("Help")

    if not n:
        routerLines.append("}")

    return routerLines


goFiles: list = getFiles()

if BUILD_FILE_NAME in goFiles:
    goFiles.remove(BUILD_FILE_NAME)

buildImports = getImports(goFiles)
buildRouter = createRouter(goFiles)
buildFileContent = [
    f"package {path.basename(ROUTES_PATH)}",
    "",
    "import (",
    *buildImports,
    ")",
    "",
    *buildRouter,
]

buildFile = open(path.join(CWD, SRC_DIR, ROUTES_PATH, BUILD_FILE_NAME + ".go"), "w")
buildFile.write(joiner(buildFileContent))
buildFile.close()

print("Success")