FROM ${CI_REPOSITORY}/base

WORKDIR /root/rpmbuild


COPY . BUILD/ovp-idv-ha

RUN rpmbuild --define="VCS_VERSION ${CI_VERSION}" --define="VCS_RELEASE ${CI_RELEASE}" \
        -bb BUILD/ovp-idv-ha/ovp-idv-ha.spec && \
    rm -rf {BUILD,BUILDROOT,SOURCES,SPECS}