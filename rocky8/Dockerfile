FROM @BASE_IMAGE_NAME@

RUN dnf install -y @DEFAULT_PACKAGES@ bash automake bzip2 bzip2-libs bzip2-devel \
      file file-libs fontconfig freetype gcc-c++  git glibc krb5-libs libaio \
      libcom_err libgomp libICE libidn \
      libSM libX11 libX11-devel libxcrypt libXcursor libXext \
      libXft libXi libXinerama \
      libXmu libXpm libXpm-devel libXrandr libXrender \
      java-1.8.0-openjdk-devel libtool m4 make \
      ncurses ncurses-libs ncurses-devel nspr nss nss-util \
      openssl openssl-devel openssl-libs \
      perl perl-interpreter perl-libs \
      perl-Carp perl-constant perl-Data-Dumper perl-DBI \
      perl-Digest-MD5 perl-Encode perl-Env perl-Exporter perl-ExtUtils-Embed \
      perl-File-Path perl-File-Temp perl-Getopt-Long perl-IO perl-libnet \
      perl-Memoize perl-PathTools perl-Scalar-List-Utils perl-Socket perl-Storable \
      perl-Term-ANSIColor perl-Test-Harness perl-Text-ParseWords perl-Thread-Queue \
      perl-Time-HiRes perl-Time-Local perl-YAML \
      patch popt python2 python3 readline rpm-build \
      rsync tcl time tk wget which zlib \
      bc tar zip unzip hostname nano procps-ng dnf-plugins-core python3-requests \
      libnsl e2fsprogs e2fsprogs-libs libXext-devel libXft-devel \
      libglvnd-opengl mesa-libGLU mesa-libGLU-devel nss-devel perl-CGI \
      popt-devel readline-devel tcsh zsh tcl-devel tk-devel strace \
      krb5-workstation python2-requests environment-modules &&\
    dnf install -y epel-release &&\
    dnf install -y @EPEL_PACKAGES@ voms-clients-cpp python2-psutil myproxy apptainer &&\
    dnf update -y ca-certificates &&\
    dnf config-manager --set-enabled powertools &&\
    dnf install -y libstdc++-static &&\
    ([ "@EXTRA_PACKAGES@" != "" ] && dnf -y install @EXTRA_PACKAGES@ || true) &&\
    alternatives --set python `which python2` &&\
    echo el8 > /etc/cmsos &&\
    dnf clean all

ADD share/krb5.conf /etc/krb5.conf
ADD share/ca-bundle.crt /etc/pki/tls/certs/ca-bundle.crt
ADD share/fix_ssh_config.sh /tmp/fix_ssh_config.sh
RUN mkdir -p /cvmfs /afs /eos /etc/vomses /etc/grid-security /build /data /pool /opt/cms &&\
    touch /etc/tnsnames.ora &&\
    /tmp/fix_ssh_config.sh /etc/ssh/ssh_config && rm -f /tmp/fix_ssh_config.sh &&\
    sed -i -e s'|^ *allow  *setuid.*|allow setuid = no|;s|^ *enable  *overlay.*|enable overlay = no|;s|^ *enable  *underlay.*|enable underlay = yes|' /etc/apptainer/apptainer.conf
