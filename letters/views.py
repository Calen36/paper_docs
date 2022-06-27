from .scripts import *
from django.template import loader
from django.shortcuts import get_object_or_404


# def show_family(request, pk):
#     letter = get_object_or_404(BaseLetter, pk=pk)
#     root_msg = letter.get_root()
#     results = letter.get_root().get_descendants(include_self=True)
#     context = {'stuff': results, 'message': root_msg}
#     return render(request, template_name='letters/index.html', context=context)


def get_extended_letter_url(request, tail):
    pk = tail.split('/')[0]
    object = get_object_or_404(BaseLetter, pk=pk)
    return redirect(object.get_extension_url())


def get_extended_ctrp_url(request, tail):
    pk = tail.split('/')[0]
    object = get_object_or_404(Counterparty, pk=pk)
    return redirect(object.get_extension_url())