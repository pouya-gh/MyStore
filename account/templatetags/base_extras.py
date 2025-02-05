from django import template

register = template.Library()

@register.simple_tag
def make_lang_selection_url(current_url: str, current_lang: str, new_lang: str):
    if current_url.startswith("/" + current_lang + "/") and current_lang != new_lang:
        return current_url.replace("/" + current_lang + "/", "/" + new_lang + "/")
    else:
        return current_url