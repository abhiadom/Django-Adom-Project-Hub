import subprocess
import time

import docker
import socket
import os

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseNotAllowed
from .forms import ProjectForm
from .models import Project


def home(request):
    return render(request, 'home.html', {})


def my_projects(request):
    projects = Project.objects.filter(creator=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            new_project = form.save(commit=False)
            new_project.creator = request.user
            new_project.save()
            return redirect('projects')
    else:
        form = ProjectForm()
    return render(request, 'projects.html', {'projects': projects, 'form': form})


def project_display(request, project_id):
    project = get_object_or_404(Project, id=project_id, creator=request.user)
    container_status = 'Stopped'
    if project.container_id:
        client = docker.from_env()
        try:
            container = client.containers.get(project.container_id)
            if container.status == 'running':
                container_status = 'Running'
        except docker.errors.NotFound:
            container_status = 'Stopped'

    server_ip = get_server_ip()

    context = {
        'project': project,
        'container_status': container_status,
        'server_ip': server_ip,
    }
    return render(request, 'project_display.html', context)


def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, creator=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return render(request, 'project_display.html', {'project': project})
    else:
        form = ProjectForm(instance=project)
    return render(request, 'edit_project.html', {'form': form, 'project': project})

# Work on adding the functionality to delete the file system as well.
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id, creator=request.user)
    if request.method == 'POST':
        project.delete()
        return redirect('projects')
    return HttpResponseNotAllowed(['POST'])


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def get_server_ip():
   server_ip = socket.gethostbyname(socket.gethostname())
   return server_ip


def run_container(request, project_id):
    project = get_object_or_404(Project, id=project_id, creator=request.user)
    try:
        client = docker.from_env()
        free_port_ssh = get_free_port()
        free_port_code_server = get_free_port()
        workspace_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'workspace').replace('\\', '/')
        uf2_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'uf2').replace('\\', '/')
        project_folder = os.path.join(workspace_path, project.name).replace('\\', '/')

        # Ensure the project folder exists
        if not os.path.exists(project_folder):
            os.makedirs(project_folder, exist_ok=True)
            repo_url = "https://github.com/abhiadom/RP2040_ProjectC.git" if project.language == 'C' else "https://github.com/abhiadom/RP2040_ProjectPy.git"
            subprocess.run(["git", "clone", repo_url, project_folder], check=True)


        server_ip = get_server_ip()

        container = client.containers.run(
            image='rp2040-dev-env:latest',
            name=f'rp2040-container-{project.id}',
            ports={'22/tcp': (server_ip, free_port_ssh), '8080/tcp': ('0.0.0.0', free_port_code_server)},
            volumes={
                project_folder: {'bind': '/workspace', 'mode': 'rw'},
                uf2_folder: {'bind': '/mnt/d_drive', 'mode': 'rw'}
            },
            devices=['/dev/bus/usb:/dev/bus/usb'],
            detach=True,
            tty=True,
            stdin_open=True,
            privileged=True,
            command=["/bin/sh", "-c", "/usr/sbin/sshd -D & code-server --bind-addr 0.0.0.0:8080 /workspace"]
        )
        project.container_id = container.id
        project.port = str(free_port_ssh)
        project.code_server_port = str(free_port_code_server)
        project.save()
    except docker.errors.DockerException as e:
        print(f"Error starting Docker container: {e}")
    return redirect('project_display', project_id=project.id)


def stop_container(request, project_id):
    project = get_object_or_404(Project, id=project_id, creator=request.user)
    try:
        client = docker.from_env()
        container = client.containers.get(project.container_id)
        container.stop()
        container.remove()
        project.container_id = ''
        project.port = ''
        project.code_server_port = ''  # Clear the code_server_port
        project.save()
    except docker.errors.DockerException as e:
        print(f"Error stopping Docker container: {e}")
    return redirect('project_display', project_id=project.id)

def send_file(request, project_id):
    uf2_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'uf2').replace('\\', '/')
    os.system("copy \"C:/Users/Adom/Desktop/uf2/\" \"D:/\"")
    os.system("del /Q \"C:/Users/Adom/Desktop/uf2/\"")
    # os.system("del /Q " + uf2_folder)
    time.sleep(2)
    if not os.path.exists(uf2_folder):
        os.makedirs(uf2_folder)
    return redirect('project_display', project_id=project_id)

