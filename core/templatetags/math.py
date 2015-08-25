from django import template

register = template.Library()

def mult(value, arg):
    "Multiplies the arg and the value"
    return float(value) * float(arg)
    
def sub(value, arg):
    "Subtracts the arg from the value"
    return float(value) - float(arg)
    
def div(value, arg):
    "Divides the value by the arg"
    return float(value) / float(arg)
    
register.filter('mult', mult)
register.filter('sub', sub)
register.filter('div', div)
