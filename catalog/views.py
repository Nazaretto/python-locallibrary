from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import Http404
from django.shortcuts import render
from django.views import generic
from .models import Book, Author, BookInstance, Genre
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime
from .forms import RenewBookForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author


def index(request):
    """
    View function for home page of site.
    """
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()  # The 'all()' is implied by default.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'catalog/index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_authors': num_authors, 'num_visits':num_visits},
    )


class BooksListView(generic.ListView):
    model = Book
    paginate_by = 10
    # context_object_name = 'my_book_list'  # ваше власне ім’я змінної контесту у шаблоні
    # def get_query(self):
    # def get_context_data(self, **kwargs):
    #     # у першу чергу отримуємо базову реалізацію контексту
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     # додаємо нову змінну до контексту та ініціалізуємо її деякими значеннями
    #     context['some_data'] = 'This is just some data'
    #     return context


class AuthorListView(generic.ListView):
    model = Author


class AuthorDetailView(generic.DetailView):
    model = Author

    def author_detail_view(request, pk):
        try:
            author_id = Author.objects.get(pk=pk)
        except Book.DoesNotExist:
            raise Http404("Book does nxot exist")

        return render(
            request,
            'catalog/author_detail.html',
            context={'author': author_id, }
        )


class BookDetailView(generic.DetailView):
    model = Book
    paginate_by = 4

    def book_detail_view(request, pk):
        try:
            book_id = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            raise Http404("Book does not exist")

        # book_id=get_object_or_404(Book, pk=pk)

        return render(
            request,
            'catalog/book_detail.html',
            context={'book': book_id, }
        )


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/list_borrowed_books.html'
    context_object_name = 'loaned_list'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_inst = get_object_or_404(BookInstance, pk = pk)

    # Якщо даний запит типу POST, тоді
    if request.method == 'POST':

        # Створюємо примірник форми, заповнюємо даними з запиту (зв'язування, binding):
        form = RenewBookForm(request.POST)

        # Проверка валидности данных формы:
        if form.is_valid():
            # Обробка даних з form.cleaned_data
            # (тут ми просто присвоюємо їх полю due_back)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # Перехід за адресою 'all-borrowed':
            return HttpResponseRedirect(reverse('all-borrowed'))

    # Якщо це GET (або який-небудь ще), створити форму за замовчуванням.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})


class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'12/10/2016',}


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('author')


class BookCreate(CreateView):
    model = Book
    fields = '__all__'


class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
