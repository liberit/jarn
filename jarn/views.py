from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse
from django.template import RequestContext
from jarn.forms import UploadForm
from jarn.odt import ODT
from jarn.models import Document


def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))

def documents(request):
    docs = Document.objects.all()
    return render_to_response('documents.html', {'documents': docs}, context_instance=RequestContext(request))

def document(request, doc_id):
    doc = Document.objects.get(id__exact=doc_id)
    return render_to_response('document.html', {'document': doc}, context_instance=RequestContext(request))

@login_required(login_url='/login')
def upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            if f.name.endswith('.odt'):
                odt = ODT(f)
                d = Document(title=form.cleaned_data['name'], html=odt.html(), author=request.user)
                d.save()
                return HttpResponse(odt.json())
            return redirect('/')
    else:
        form = UploadForm()
    return render_to_response('upload.html', {'form': form}, context_instance=RequestContext(request))


@login_required(login_url='/login')
def logout_redirect(request):
    logout(request)
    return redirect('/')
