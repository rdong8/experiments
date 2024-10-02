set dotenv-load

project := "experiments"

# Path to Python executable
python := "python"
pip := python + " -m pip"

init:
    {{ pip }} install --upgrade -e .[dev] 

run:
    {{ python }} -m {{ project }}

clean:

# Kubernetes

chart := "charts/experiments"
image := "experiments"
user := "rdong8tristero"
repo := user / image
tag := `git rev-parse --short HEAD`
full_name := repo + ":" + tag
image_builder := "podman"
secret_name := "experiments-secret"
env_file := ".env"
values := "values/values.yaml"

namespace := "test"
release := "experiments"

build-image cache="1":
    {{ image_builder }} build . -t {{ full_name }} \
        {{ if cache == "1" { "" } else { "--no-cache" } }}

push-image:
    {{ image_builder }} push {{ full_name }}

login:
    {{ image_builder }} login -u {{ user }} docker.io/{{ repo }}

secret:
    kubectl create secret generic {{ secret_name }} -n {{ namespace }} \
        --from-env-file={{ env_file }}

delete-secret:
    kubectl delete secret {{ secret_name }} -n {{ namespace }}

install:
    helm \
        upgrade \
        -i \
        -n {{ namespace }} \
        --create-namespace \
        -f {{ values }} \
        --set image.tag={{ tag }} \
        {{ release }} \
        {{ chart }}

uninstall:
    helm \
        uninstall \
        -n {{ namespace }} \
        {{ release }}
