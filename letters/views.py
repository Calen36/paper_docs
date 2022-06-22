from .scripts import *
from django.template import loader
from django.shortcuts import get_object_or_404

def show_family(request, pk):
    letter = get_object_or_404(BaseLetter, pk=pk)
    root_msg = letter.get_root()
    results = letter.get_root().get_descendants(include_self=True)
    context = {'stuff': results, 'message': root_msg}
    return render(request, template_name='letters/index.html', context=context)


