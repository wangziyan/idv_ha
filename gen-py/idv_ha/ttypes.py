#
# Autogenerated by Thrift Compiler (0.9.1)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException

from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None



class DiskInfo:
  """
  Attributes:
   - storage_name
   - volume_name
   - size
   - type
   - content
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'storage_name', None, None, ), # 1
    (2, TType.STRING, 'volume_name', None, None, ), # 2
    (3, TType.DOUBLE, 'size', None, None, ), # 3
    (4, TType.STRING, 'type', None, None, ), # 4
    (5, TType.STRING, 'content', None, None, ), # 5
  )

  def __init__(self, storage_name=None, volume_name=None, size=None, type=None, content=None,):
    self.storage_name = storage_name
    self.volume_name = volume_name
    self.size = size
    self.type = type
    self.content = content

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.storage_name = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.volume_name = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.DOUBLE:
          self.size = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.type = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.STRING:
          self.content = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('DiskInfo')
    if self.storage_name is not None:
      oprot.writeFieldBegin('storage_name', TType.STRING, 1)
      oprot.writeString(self.storage_name)
      oprot.writeFieldEnd()
    if self.volume_name is not None:
      oprot.writeFieldBegin('volume_name', TType.STRING, 2)
      oprot.writeString(self.volume_name)
      oprot.writeFieldEnd()
    if self.size is not None:
      oprot.writeFieldBegin('size', TType.DOUBLE, 3)
      oprot.writeDouble(self.size)
      oprot.writeFieldEnd()
    if self.type is not None:
      oprot.writeFieldBegin('type', TType.STRING, 4)
      oprot.writeString(self.type)
      oprot.writeFieldEnd()
    if self.content is not None:
      oprot.writeFieldBegin('content', TType.STRING, 5)
      oprot.writeString(self.content)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class NetInfo:
  """
  Attributes:
   - vip
   - rid
   - master_ip
   - backup_ip
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'vip', None, None, ), # 1
    (2, TType.STRING, 'rid', None, None, ), # 2
    (3, TType.STRING, 'master_ip', None, None, ), # 3
    (4, TType.STRING, 'backup_ip', None, None, ), # 4
  )

  def __init__(self, vip=None, rid=None, master_ip=None, backup_ip=None,):
    self.vip = vip
    self.rid = rid
    self.master_ip = master_ip
    self.backup_ip = backup_ip

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.vip = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.rid = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.master_ip = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.backup_ip = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('NetInfo')
    if self.vip is not None:
      oprot.writeFieldBegin('vip', TType.STRING, 1)
      oprot.writeString(self.vip)
      oprot.writeFieldEnd()
    if self.rid is not None:
      oprot.writeFieldBegin('rid', TType.STRING, 2)
      oprot.writeString(self.rid)
      oprot.writeFieldEnd()
    if self.master_ip is not None:
      oprot.writeFieldBegin('master_ip', TType.STRING, 3)
      oprot.writeString(self.master_ip)
      oprot.writeFieldEnd()
    if self.backup_ip is not None:
      oprot.writeFieldBegin('backup_ip', TType.STRING, 4)
      oprot.writeString(self.backup_ip)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class DrbdInfo:
  """
  Attributes:
   - res_num
   - port_num
   - primary_host
   - secondary_host
   - block_dev
   - is_external
   - metedata
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'res_num', None, None, ), # 1
    (2, TType.I32, 'port_num', None, None, ), # 2
    (3, TType.STRING, 'primary_host', None, None, ), # 3
    (4, TType.STRING, 'secondary_host', None, None, ), # 4
    (5, TType.STRING, 'block_dev', None, None, ), # 5
    (6, TType.BOOL, 'is_external', None, None, ), # 6
    (7, TType.STRING, 'metedata', None, None, ), # 7
  )

  def __init__(self, res_num=None, port_num=None, primary_host=None, secondary_host=None, block_dev=None, is_external=None, metedata=None,):
    self.res_num = res_num
    self.port_num = port_num
    self.primary_host = primary_host
    self.secondary_host = secondary_host
    self.block_dev = block_dev
    self.is_external = is_external
    self.metedata = metedata

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I32:
          self.res_num = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I32:
          self.port_num = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.primary_host = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.secondary_host = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.STRING:
          self.block_dev = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 6:
        if ftype == TType.BOOL:
          self.is_external = iprot.readBool();
        else:
          iprot.skip(ftype)
      elif fid == 7:
        if ftype == TType.STRING:
          self.metedata = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('DrbdInfo')
    if self.res_num is not None:
      oprot.writeFieldBegin('res_num', TType.I32, 1)
      oprot.writeI32(self.res_num)
      oprot.writeFieldEnd()
    if self.port_num is not None:
      oprot.writeFieldBegin('port_num', TType.I32, 2)
      oprot.writeI32(self.port_num)
      oprot.writeFieldEnd()
    if self.primary_host is not None:
      oprot.writeFieldBegin('primary_host', TType.STRING, 3)
      oprot.writeString(self.primary_host)
      oprot.writeFieldEnd()
    if self.secondary_host is not None:
      oprot.writeFieldBegin('secondary_host', TType.STRING, 4)
      oprot.writeString(self.secondary_host)
      oprot.writeFieldEnd()
    if self.block_dev is not None:
      oprot.writeFieldBegin('block_dev', TType.STRING, 5)
      oprot.writeString(self.block_dev)
      oprot.writeFieldEnd()
    if self.is_external is not None:
      oprot.writeFieldBegin('is_external', TType.BOOL, 6)
      oprot.writeBool(self.is_external)
      oprot.writeFieldEnd()
    if self.metedata is not None:
      oprot.writeFieldBegin('metedata', TType.STRING, 7)
      oprot.writeString(self.metedata)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class NodeInfo:
  """
  Attributes:
   - hostname
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'hostname', None, None, ), # 1
  )

  def __init__(self, hostname=None,):
    self.hostname = hostname

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.hostname = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('NodeInfo')
    if self.hostname is not None:
      oprot.writeFieldBegin('hostname', TType.STRING, 1)
      oprot.writeString(self.hostname)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
