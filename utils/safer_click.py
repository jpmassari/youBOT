from utils.mouse_lerp import lerp

def safer_click(element):
    x, y = element.location['x'], element.location['y']
    lerp(x, y)
    element.click_safe()
