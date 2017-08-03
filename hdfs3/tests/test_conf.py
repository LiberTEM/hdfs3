
import os
import pytest
import shutil
import tempfile
from hdfs3.conf import conf, guess_config, conf_defaults, hdfs_conf
from hdfs3 import HDFileSystem


@pytest.yield_fixture()
def no_conf():
    # clear environment
    os.environ.pop('HADOOP_CONF_DIR', '')
    os.environ.pop('HADOOP_INSTALL', '')
    os.environ.pop('LIBHDFS3_CONF', '')
    yield


@pytest.yield_fixture()
def simple_conf_file(no_conf):
    d = tempfile.mkdtemp()
    fn = os.path.join(d, 'hdfs-site.xml')
    with open(fn, 'w') as fout:
        fout.write(example_conf)
    yield fn
    shutil.rmtree(d, True)


def test_no_conf(no_conf):
    if 'host' in conf:
        assert conf['host'] is not None
    if 'port' in conf:
        assert conf['port'] is not None


def test_with_libhdfs3_conf(simple_conf_file):
    os.environ['LIBHDFS3_CONF'] = simple_conf_file
    guess_config()
    assert conf['host'] == 'this.place'
    assert conf['port'] == 9999
    assert conf['dfs.replication'] == '1'


def test_with_hadoop_conf(simple_conf_file):
    dname = os.path.dirname(simple_conf_file)
    os.environ['HADOOP_CONF_DIR'] = dname
    guess_config()
    assert os.environ['LIBHDFS3_CONF'] == simple_conf_file
    assert conf['host'] == 'this.place'
    assert conf['port'] == 9999
    assert conf['dfs.replication'] == '1'


def test_with_file(simple_conf_file):
    hdfs_conf(simple_conf_file)
    assert conf['host'] == 'this.place'
    assert conf['port'] == 9999
    assert conf['dfs.replication'] == '1'


def test_default_port_and_host(no_conf):
    guess_config()
    hdfs = HDFileSystem(connect=False)
    assert hdfs.host == conf_defaults['host']
    assert hdfs.port == conf_defaults['port']


def test_token_and_ticket_cache_in_same_time():
    ticket_cache = "/tmp/krb5cc_0"
    token = "abc"

    with pytest.raises(RuntimeError) as ctx:
        HDFileSystem(connect=False, ticket_cache=ticket_cache, token=token)

    msg = "It is not possible to use ticket_cache and token at same time"
    assert msg in str(ctx.value)


example_conf = """
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>

<configuration>

  <property>
    <name>dfs.namenode.rpc-address</name>
    <value>this.place:9999</value>
  </property>

  <property>
    <name>dfs.replication</name>
    <value>1</value>
  </property>

  <property>
    <name>dfs.blocksize</name>
    <value>134217728</value>
  </property>

  <property>
    <name>dfs.permissions</name>
    <value>false</value>
  </property>

  <property>
    <name>dfs.client.read.shortcircuit</name>
    <value>true</value>
  </property>

  <property>
    <name>dfs.domain.socket.path</name>
    <value>/var/lib/hadoop-hdfs/dn_socket</value>
  </property>

  <property>
    <name>dfs.client.read.shortcircuit.skip.checksum</name>
    <value>true</value>
  </property>

  <property>
     <name>dfs.webhdfs.enabled</name>
     <value>false</value>
  </property>
</configuration>
"""