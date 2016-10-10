require 'date'

Vagrant.require_version ">= 1.5.1"

def setup_mountpoint(config, app, path)
  config.vm.synced_folder path, "/#{app}"
end

Vagrant.configure("2") do |config|
  config.vm.define "webrtc-local" do |c|
    c.vm.provider "virtualbox"
    c.vm.box = "ubuntu/trusty64"

    c.vm.provider :virtualbox do |virtualbox|
      virtualbox.name = "webrtc-dev"
    end

    config.ssh.forward_agent = true

    setup_mountpoint(config, "webrtc", ".")

    config.vm.network "forwarded_port", guest: 5347, host: 5347

    c.vm.provision :ansible do |ansible|
      ansible.playbook = "provisioning/site.yml"
      ansible.verbose = 'v'
      ansible.extra_vars = {
      }
    end
  end
end
