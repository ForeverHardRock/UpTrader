from django import template
from django.db.models import Prefetch
from menu.models import Menu, MenuItem
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def draw_menu(context, menu_url):
    current_path = context['request'].path

    try:

        # получаем меню
        menu = Menu.objects.prefetch_related(
            Prefetch(
                'items',
                queryset=MenuItem.objects.select_related('parent').all()
            )
        ).get(url=menu_url)

        # строим дерево
        items, root = tree_build(menu)

        # определяем активный путь
        active_item = get_active_path(items, current_path)

        # определяем развернутые
        if active_item:
            for node in root:
                if mark_expanded(node, active_item):
                    break

        # рендерим html
        base_url = f'/menu/{menu_url}'
        return mark_safe(render_nodes(root, base_url, current_path))

    except Menu.DoesNotExist:
        menus = Menu.objects.all()
        context = '<ul>'
        for menu in menus:
            context += f"<li><a href='{menu.url}'>{menu.name}</a></li>"
        context += '</ul>'
        return mark_safe(context)


def tree_build(menu):
    """ Строит дерево. """
    items = menu.items.all()
    menu_dict = {}
    for item in items:
        menu_dict[item.id] = {
            'item': item,
            'children': [],
            'expanded': False,
            'active': False
        }
    root = []
    for item in items:
        if item.parent_id:
            parent = menu_dict.get(item.parent_id)
            if parent:
                parent['children'].append(menu_dict[item.id])
        else:
            root.append(menu_dict[item.id])

    return items, root


def get_active_path(items, current_path):
    """ Получает активный путь. """

    active_item = None
    for item in items:
        if item.get_url() == current_path:
            active_item = item
            break
    return active_item


def mark_expanded(node, active, level=0):
    """ Определяет, должен ли быть развернут узел. """
    if level > 1:
        return False
    node['expanded'] = False
    node['active'] = False
    if node['item'] == active:
        node['active'] = True
        node['expanded'] = True
        return True
    for child in node['children']:
        if mark_expanded(child, active, level + 1):
            node['expanded'] = True
    return node['expanded']


def build_full_url(base_url, item):
    """ Строит полный URL для элемента меню. """
    if item['item'].url:
        return f'{base_url}/{item["item"].url}'
    return base_url


def render_nodes(nodes, base_url, current_path):
    """ Рендерит узлы меню в HTML. """
    html = '<ul>'
    for node in nodes:
        full_url = build_full_url(base_url, node)
        classes = []
        if full_url == current_path:
            classes.append('active')
        if node['expanded']:
            classes.append('expanded')
        class_attr = f' class="{" ".join(classes)}"' if classes else ''
        html += f'<li{class_attr}>'
        html += f'<a href="{full_url}">{node["item"].title}</a>'
        if node['expanded']:
            html += render_nodes(node['children'], full_url, current_path)
        html += '</li>'
    html += '</ul>'
    return html

