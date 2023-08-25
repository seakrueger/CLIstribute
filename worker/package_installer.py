import apt
import logging

logger = logging.getLogger("worker")

def packages(pkgs):
    if not pkgs:
        return

    apt_cache = apt.Cache()
    apt_cache.update()
    apt_cache.open()

    for pkg_name in pkgs:
        pkg = apt_cache[pkg_name]
        if not pkg.is_installed:
            pkg.mark_install()
            logger.info(f"Installing {pkg_name}")
        else:
            logger.info(f"{pkg_name} is already installed")

    try:
        apt_cache.commit()
    except Exception as e:
        logger.error("Failed to install packages", e)

    apt_cache.close()