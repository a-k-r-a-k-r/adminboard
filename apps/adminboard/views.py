from django.shortcuts import render, redirect
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import TodoList
from django.core.files.storage import FileSystemStorage
import os
from django.contrib import messages
import pandas as pd
import json
from .utils import process_data
from django.contrib.auth.models import User



# helper functions
def read_csv_file(filepath, n_cluster):
    global row_no, column_no, csv_data, my_file, missing_values_no, csv_data_head, column_headers
    global count_for_pie, silh, chart, elbow, unaltered_data, graph_items, unaltered_data_csv
    my_file = pd.read_csv(filepath, engine='python')
    my_file_copy = pd.read_csv(filepath, engine='python')
    unaltered_data_csv = pd.read_csv(filepath, engine='python')
    silh, chart, elbow, processed_labels, graph_items = process_data(my_file, n_cluster)
    unaltered_data_csv['Custer_label'] = processed_labels
    csv_data = pd.DataFrame(data=my_file_copy, index=None)
    row_no = len(csv_data.axes[0])
    column_no = len(csv_data.axes[1])
    null_data = csv_data[csv_data.isnull().any(axis=1)]
    missing_values_no = len(null_data)
    # csv_data_head = csv_data.to_html()
    # parsing the DataFrame in json format.
    json_records = csv_data.reset_index().to_json(orient='records')
    csv_data_head = []
    csv_data_head = json.loads(json_records)
    column_headers = my_file.columns.tolist()
    global processed_table_data, processed_column_headers
    unaltered_data = pd.DataFrame(data=unaltered_data_csv, index=None)
    processed_json_records = unaltered_data.reset_index().to_json(orient='records')
    processed_table_data = []
    processed_table_data = json.loads(processed_json_records)
    processed_column_headers = unaltered_data_csv.columns.tolist()
    count_for_pie = {}
    for headers in column_headers:
        individual = {}
        x = csv_data[headers]
        data = list(dict(x.value_counts()).values())
        labels = list(dict(x.value_counts()).keys())
        if len(labels) > 15:
            continue
        for i in range(len(data)):
            individual[labels[i]] = data[i]
        count_for_pie[headers] = individual




# Create your views here.
@login_required(login_url="/login/")
def index(request):
    todo_items = TodoList.objects.filter(user=request.user).filter(completed = False)
    todo_completed = TodoList.objects.filter(user=request.user).filter(completed = True)
    no_of_tasks = len(todo_items)
    no_of_completed = len(todo_completed)
    context = {'segment': 'index', 'todo_items' : todo_items, 'number' : no_of_tasks, 'todo_completed': todo_completed, 'no_of_completed': no_of_completed}

    html_template = loader.get_template('adminboard/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    csv_upload_success = False

    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        try:
            user_n_cluster = int(request.POST.get('userncluster'))
        except:
            user_n_cluster = 0
        # to allow only csv file
        if uploaded_file.name.endswith('.csv'):
            # save the file in media folder
            savefile = FileSystemStorage()
            name = savefile.save(uploaded_file.name, uploaded_file)

            # know where to save the csv to
            d = os.getcwd()
            global file_directory
            file_directory = d+'\\media\\' + name
            csv_upload_success = True
            messages.success(request, 'File Uploaded Successfully')
            read_csv_file(file_directory, user_n_cluster)

            context['no_of_rows'] = row_no
            context['no_of_columns'] = column_no
            context['no_of_missing'] = missing_values_no
            context['csv_data_head'] = csv_data_head
            context['column_headers'] = column_headers
            context['processed_column_headers'] = processed_column_headers
            context['processed_table_data'] = processed_table_data
            context['null_data_distribution_keys'] = list(dict(csv_data.isnull().sum()).keys())
            context['null_data_distribution_values'] = list(dict(csv_data.isnull().sum()).values())


            new_pie_data = {}
            for key, value in count_for_pie.items():
                new_pie_data[key] = {'labellist':list(value.keys()), 'datalist':list(value.values())}
            context['count_for_pie'] = new_pie_data
            request.session['chart'] = chart
            request.session['elbow'] = elbow
            request.session['silh'] = silh
            context['silh'] = silh
            context['chart'] = chart
            context['elbow'] = elbow
            request.session['csv_data_head'] = csv_data_head
            request.session['column_headers'] = column_headers
            request.session['processed_table_data'] = processed_table_data
            request.session['processed_column_headers'] = processed_column_headers
            request.session['graph_items'] = graph_items
        else:
            messages.warning(request, 'Wrong File Type: Upload CSV file only')

    context['csv_upload_success'] = csv_upload_success
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template
        html_template = loader.get_template('adminboard/' + load_template )
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('adminboard/page-404.html')
        return HttpResponse(html_template.render(context, request))
    except:
        html_template = loader.get_template('adminboard/page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def changecompleted(request, todo_id):
    todo = TodoList.objects.get(pk=todo_id)
    if todo.completed:
        todo.completed = False
    elif not todo.completed:
        todo.completed = True
    todo.save()
    return redirect('index')


@login_required(login_url="/login/")
def showsegmentationresult(request):
    context = {}
    load_template = request.path.split('/')[-1]
    context['segment'] = load_template
    try:
        context['chart'] = request.session['chart']
        context['silh'] = request.session['silh']
        context['graph_items'] = request.session['graph_items']
    except:
        messages.warning(request, 'Upload a File to view the Segmentation')
    return render(request, 'adminboard/result.html', context)


@login_required(login_url="/login/")
def showtables(request):
    context = {}
    load_template = request.path.split('/')[-1]
    context['segment'] = load_template
    try:
        context['csv_data_head'] = request.session['processed_table_data']
        context['column_headers'] = request.session['processed_column_headers']
    except:
        messages.warning(request, 'Upload a File to view the content')
    return render(request, 'adminboard/tables.html', context)

@login_required(login_url="/login/")
def user_profile(request):
    context = {}
    load_template = request.path.split('/')[-1]
    context['segment'] = load_template
    current_user = User.objects.get(pk=request.user.id)

    if request.method == 'POST':
        user_fname = request.POST.get('user_fname', False)
        user_lname = request.POST.get('user_lname', False)
        user_address = request.POST.get('user_address', False)
        user_country = request.POST.get('user_country', False)
        user_zip = request.POST.get('user_zip', False)
        user_city = request.POST.get('user_city', False)
        user_about = request.POST.get('user_about', False)
    return render(request, 'adminboard/user-profile.html', context)


