ARG WORK_DIR=/data
ARG INSTALLER_ISO=https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/pre-release/latest-4.6/rhcos-live.x86_64.iso

#FROM quay.io/ocpmetal/livecd-iso:rhcos-livecd as livecd-build
#RUN chmod 644 /root/image/livecd.iso

FROM quay.io/coreos/coreos-installer:release AS installer-image
FROM registry.access.redhat.com/ubi8/ubi-minimal

ENV COREOS_IMAGE=$WORK_DIR/livecd.iso
ENV WORK_DIR=$WORK_DIR

RUN mkdir $WORK_DIR
RUN chmod 775 $WORK_DIR

RUN curl $INSTALLER_ISO -o ${WORK_DIR}/livecd.iso
RUN chmod 644 ${WORK_DIR}/livecd.iso
#RUN if [ -z "$LOCAL_ISO" ]; then export COPY_ORIGIN="--from=livecd-build /root/image/livecd.iso"; else export COPY_ORIGIN="$LOCAL_ISO"; fi
#COPY ${COPY_ORIGIN} ${WORK_DIR}
COPY --from=installer-image /usr/sbin/coreos-installer $WORK_DIR
ENTRYPOINT sleep infinity
