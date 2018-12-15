DIANA2 xArch Docker Image
==========================

Derek Merck  
<derek_merck@brown.edu>  
Rhode Island Hospital and Brown University  
Providence, RI  

Build multi-arch [DIANA][] Python Docker images for embedded systems.

[DIANA]:https://github.com/derekmerck/diana2


Use It
----------------------

These images are manifested per modern Docker.io guidelines so that an appropriately architected image can be will automatically selected for a given tag depending on the pulling architecture.

```bash
$ docker run derekmerck/diana2           # (latest-amd64, latest-arm32v7, latest-arm64v8)
```

Images for specific architectures images can be directly pulled from the same namespace using the format `derekmerck/diana2:${TAG}-${ARCH}`, where `$ARCH` is one of `amd64`, `arm32v7`, or `arm64v8`.  Explicit architecture specification is sometimes helpful when an indirect build service shadows the production architecture.


Build It
--------------

These images are based on the cross-platform `resin/${ARCH}-debian:buster` image.  [Resin.io][] base images include the [QEMU][] cross-compiler to facilitate building Docker images for low-power single-board computers while using more powerful Intel-architecture compute servers.

[Resin.io]: http://resin.io
[QEMU]: https://www.qemu.org

This supports builds for `amd64`, `armhf`/`arm32v7`, and `aarch64`/`arm64v8` architectures.  Most low-power single board computers such as the [Raspberry Pi][] and [Beagleboard][] are `armhf`/`arm32v7` devices.  The [Pine64][] and [NVIDIA Jetson][] are `aarch64`/`arm64v8` devices.  Desktop computers/vms, [UP boards][], and the [Intel NUC][] are `amd64` devices.  

[UP boards]: http://www.up-board.org/upcore/
[Intel NUC]: https://www.intel.com/content/www/us/en/products/boards-kits/nuc.html
[Raspberry Pi]: https://www.raspberrypi.org
[Beagleboard]: http://beagleboard.org
[Pine64]: https://www.pine64.org
[NVIDIA Jetson]: https://developer.nvidia.com/embedded/buy/jetson-tx2

`docker-compose.yml` contains build recipes for each architecture for a simple `diana` image.

To build all images:

1. Register the Docker QEMU cross-compilers
2. Call `docker-compose` to build the vanilla `diana` images
4. Get [docker-manifest][] from Github
5. Put Docker into "experimental mode" for manifest creation
6. Call `docker-manifest.py` with an appropriate domain to manifest and push the images

[docker-manifest]: https://github.com/derekmerck/docker-manifest

```bash
$ docker run --rm --privileged multiarch/qemu-user-static:register --reset
$ docker-compose build diana2-amd64 diana2-arm32v7 diana2-arm64v8
$ pip install git+https://github.com/derekmerck/docker-manifest
$ mkdir -p $HOME/.docker && echo '{"experimental":"enabled"}' > "$HOME/.docker/config.json"
$ python3 docker-manifest.py --d $DOCKER_USERNAME diana2
```

A [Travis][] automation pipeline for git-push-triggered image regeneration and tagging is demonstrated in the `.travis.yml` script.  However, these cross-compiling jobs exceed Travis' 50-minute timeout window, so builds are currently done by hand using cloud infrastructure.

[Travis]: http://travis-ci.org

```bash
$ docker run -it diana-amd64 python3 -c "import diana; print(diana.__version__)"
2.0.1
```

### DIANA on ARM
 
If you need access to an ARM device for development, [Packet.net][] rents bare-metal 96-core 128GB `aarch64` [Cavium ThunderX] servers for $0.50/hour.  Packet's affiliated [Works On Arm][] program provided compute time for developing and testing these cross-platform images.

[Cavium ThunderX]: https://www.cavium.com/product-thunderx-arm-processors.html
[Packet.net]: https://packet.net
[Works On Arm]: https://www.worksonarm.com

An `arm64v8` image can be built natively and pushed from Packet, using a brief tenancy on a bare-metal Cavium ThunderX ARMv8 server.

```bash
$ apt update && apt upgrade
$ curl -fsSL get.docker.com -o get-docker.sh
$ sh get-docker.sh 
$ docker run hello-world
$ apt install git python-pip
$ pip install docker-compose
$ git clone http://github.com/derekmerck/diana2
$ cd diana2/platform/images/diana
$ docker-compose build diana2-arm64v8
$ python3 manifest-it.py diana-xarch.manifest.yml
```

Although [Resin uses Packet ARM servers to compile arm32 images][resin-on-packet], the available ThunderX does not implement the arm32 instruction set, so it [cannot compile natively for the Raspberry Pi][no-arm32].

[Packet.io]: https://packet.io
[resin-on-packet]: https://resin.io/blog/docker-builds-on-arm-servers-youre-not-crazy-your-builds-really-are-5x-faster/
[no-arm32]: https://gitlab.com/gitlab-org/omnibus-gitlab/issues/2544

Now pull the image tag. You can confirm that the appropriate image has been pulled by starting a container with the command `arch`.  

```bash
$ docker run derekmerck/diana2 arch
aarch64
```

You can also confirm the image architecture without running a container by inspecting the value of `.Config.Labels.architecture`.  (This is a creator-defined label that is _different_ than the normal `.Architecture` key -- which appears to _always_ report as `amd64`.)

```bash
$ docker inspect derekmerck/diana2 --format "{{ .Config.Labels.architecture }}"
arm64v8
```


License
-------

MIT