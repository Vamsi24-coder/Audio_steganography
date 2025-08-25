import inspect
import gui_utils
function_names = []
for name, member in inspect.getmembers(gui_utils):
    if inspect.isfunction(member):
        function_names.append(name)

print(function_names)