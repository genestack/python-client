VERSION 0.6

ARG --required DOCKER_REGISTRY_GROUP
ARG --required GITHUB_USER
ARG --required GITHUB_USER_EMAIL

build:
    FROM ${DOCKER_REGISTRY_GROUP}/genestack-builder:latest

    COPY . .

    RUN python3 setup.py sdist
    SAVE IMAGE --cache-hint

release:
    FROM +build

    ### Get release version from version.py
    ARG RELEASE_VERSION=$(./setup.py --version)
    RUN echo --no-cache "RELEASE_VERSION=${RELEASE_VERSION}"

    ## Check that RELEASE_VERSION exists in git tags.
    ARG GIT_TAG_PRECONDITION=$(git tag -l | grep ${RELEASE_VERSION})
    IF [ -z ${GIT_TAG_PRECONDITION} ]
        RUN --no-cache echo "v${RELEASE_VERSION} wasn't found in git tags. Let's move on."
    ELSE
        RUN --no-cache echo "v${RELEASE_VERSION} was found in git tags. Stop script." && exit 1
    END

    ### Check that RELEASE_VERSION exists in ChangeLog.
    ARG CHANGE_LOG_PRECONDITION=$(grep ${RELEASE_VERSION} ChangeLog)
    IF [ -z ${CHANGE_LOG_PRECONDITION} ]
        RUN --no-cache echo "${RELEASE_VERSION} wasn't found in ChangeLog. Stop script." && exit 1
    ELSE
        RUN --no-cache echo "${RELEASE_VERSION} was found in ChangeLog. Let's move on."
    END

    # Git magic (merge master to stable and push tag)
    RUN --push --secret GITHUB_TOKEN \
        git config user.name ${GITHUB_USER} && \
        git config user.email ${GITHUB_USER_EMAIL} && \
        gh auth setup-git && \
        git fetch --all && \
        git checkout stable && \
        git merge master && \
        git checkout master && \
        git push && \
        git tag -l | xargs git tag -d && \
        git fetch --tags && \
        git tag v${RELEASE_VERSION} && \
        git push --tags

    ## Create Github release
    RUN --push --secret GITHUB_TOKEN \
        curl \
            -X POST \
            -H "Accept: application/vnd.github+json" \
            -H "Authorization: Bearer ${GITHUB_TOKEN}" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            "https://api.github.com/repos/genestack/python-client/releases" \
            -d '{"tag_name":"v'${RELEASE_VERSION}'","target_commitish":"master","name":"genestack-python-client-v'${RELEASE_VERSION}'","body":"Description of the release here: https://github.com/genestack/python-client/blob/v'${RELEASE_VERSION}'/ChangeLog","draft":false,"prerelease":false,"generate_release_notes":false}'

    ## Trigger Read the docs builds
    RUN --push --secret RTD_TOKEN \
        curl \
          -X POST \
          -H "Authorization: Token ${RTD_TOKEN}" "https://readthedocs.org/api/v3/projects/genestack-client/versions/latest/builds/" && \
        curl \
          -X POST \
          -H "Authorization: Token ${RTD_TOKEN}" "https://readthedocs.org/api/v3/projects/genestack-client/versions/stable/builds/"

    # Push to pypi
    RUN --push \
     --secret PIPY_USER_PROD \
     --secret PIPY_USER_TEST \
     --secret PIPY_PASSWORD_PROD \
     --secret PIPY_PASSWORD_TEST \
        generate-pypirc.sh && \
        twine upload dist/* -r testpypi && \
        twine upload dist/*
