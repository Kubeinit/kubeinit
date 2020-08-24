FROM quay.io/ocpmetal/livecd-iso:rhcos-livecd as livecd-build
RUN chmod 644 /root/image/livecd.iso

FROM quay.io/coreos/coreos-installer:release AS installer-image
FROM registry.access.redhat.com/ubi8/ubi-minimal

ARG WORK_DIR=/data
ENV COREOS_IMAGE=$WORK_DIR/livecd.iso
ENV WORK_DIR=$WORK_DIR

RUN mkdir $WORK_DIR
RUN chmod 775 $WORK_DIR

COPY --from=livecd-build /root/image/livecd.iso $WORK_DIR
COPY --from=installer-image /usr/sbin/coreos-installer $WORK_DIR
ENTRYPOINT sleep infinity
