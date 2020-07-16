#
# Autogenerated by Thrift Compiler (0.9.1)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
require 5.6.0;
use strict;
use warnings;
use Thrift;

package OVP::IDVHa::DiskInfo;
use base qw(Class::Accessor);
OVP::IDVHa::DiskInfo->mk_accessors( qw( storage_name volume_name size type content ) );

sub new {
  my $classname = shift;
  my $self      = {};
  my $vals      = shift || {};
  $self->{storage_name} = undef;
  $self->{volume_name} = undef;
  $self->{size} = undef;
  $self->{type} = undef;
  $self->{content} = undef;
  if (UNIVERSAL::isa($vals,'HASH')) {
    if (defined $vals->{storage_name}) {
      $self->{storage_name} = $vals->{storage_name};
    }
    if (defined $vals->{volume_name}) {
      $self->{volume_name} = $vals->{volume_name};
    }
    if (defined $vals->{size}) {
      $self->{size} = $vals->{size};
    }
    if (defined $vals->{type}) {
      $self->{type} = $vals->{type};
    }
    if (defined $vals->{content}) {
      $self->{content} = $vals->{content};
    }
  }
  return bless ($self, $classname);
}

sub getName {
  return 'DiskInfo';
}

sub read {
  my ($self, $input) = @_;
  my $xfer  = 0;
  my $fname;
  my $ftype = 0;
  my $fid   = 0;
  $xfer += $input->readStructBegin(\$fname);
  while (1) 
  {
    $xfer += $input->readFieldBegin(\$fname, \$ftype, \$fid);
    if ($ftype == TType::STOP) {
      last;
    }
    SWITCH: for($fid)
    {
      /^1$/ && do{      if ($ftype == TType::STRING) {
        $xfer += $input->readString(\$self->{storage_name});
      } else {
        $xfer += $input->skip($ftype);
      }
      last; };
      /^2$/ && do{      if ($ftype == TType::STRING) {
        $xfer += $input->readString(\$self->{volume_name});
      } else {
        $xfer += $input->skip($ftype);
      }
      last; };
      /^3$/ && do{      if ($ftype == TType::DOUBLE) {
        $xfer += $input->readDouble(\$self->{size});
      } else {
        $xfer += $input->skip($ftype);
      }
      last; };
      /^4$/ && do{      if ($ftype == TType::STRING) {
        $xfer += $input->readString(\$self->{type});
      } else {
        $xfer += $input->skip($ftype);
      }
      last; };
      /^5$/ && do{      if ($ftype == TType::STRING) {
        $xfer += $input->readString(\$self->{content});
      } else {
        $xfer += $input->skip($ftype);
      }
      last; };
        $xfer += $input->skip($ftype);
    }
    $xfer += $input->readFieldEnd();
  }
  $xfer += $input->readStructEnd();
  return $xfer;
}

sub write {
  my ($self, $output) = @_;
  my $xfer   = 0;
  $xfer += $output->writeStructBegin('DiskInfo');
  if (defined $self->{storage_name}) {
    $xfer += $output->writeFieldBegin('storage_name', TType::STRING, 1);
    $xfer += $output->writeString($self->{storage_name});
    $xfer += $output->writeFieldEnd();
  }
  if (defined $self->{volume_name}) {
    $xfer += $output->writeFieldBegin('volume_name', TType::STRING, 2);
    $xfer += $output->writeString($self->{volume_name});
    $xfer += $output->writeFieldEnd();
  }
  if (defined $self->{size}) {
    $xfer += $output->writeFieldBegin('size', TType::DOUBLE, 3);
    $xfer += $output->writeDouble($self->{size});
    $xfer += $output->writeFieldEnd();
  }
  if (defined $self->{type}) {
    $xfer += $output->writeFieldBegin('type', TType::STRING, 4);
    $xfer += $output->writeString($self->{type});
    $xfer += $output->writeFieldEnd();
  }
  if (defined $self->{content}) {
    $xfer += $output->writeFieldBegin('content', TType::STRING, 5);
    $xfer += $output->writeString($self->{content});
    $xfer += $output->writeFieldEnd();
  }
  $xfer += $output->writeFieldStop();
  $xfer += $output->writeStructEnd();
  return $xfer;
}

package OVP::IDVHa::NetInfo;
use base qw(Class::Accessor);
OVP::IDVHa::NetInfo->mk_accessors( qw( vip rid master_ip backup_ip ) );

sub new {
  my $classname = shift;
  my $self      = {};
  my $vals      = shift || {};
  $self->{vip} = undef;
  $self->{rid} = undef;
  $self->{master_ip} = undef;
  $self->{backup_ip} = undef;
  if (UNIVERSAL::isa($vals,'HASH')) {
    if (defined $vals->{vip}) {
      $self->{vip} = $vals->{vip};
    }
    if (defined $vals->{rid}) {
      $self->{rid} = $vals->{rid};
    }
    if (defined $vals->{master_ip}) {
      $self->{master_ip} = $vals->{master_ip};
    }
    if (defined $vals->{backup_ip}) {
      $self->{backup_ip} = $vals->{backup_ip};
    }
  }
  return bless ($self, $classname);
}

sub getName {
  return 'NetInfo';
}

sub read {
  my ($self, $input) = @_;
  my $xfer  = 0;
  my $fname;
  my $ftype = 0;
  my $fid   = 0;
  $xfer += $input->readStructBegin(\$fname);
  while (1) 
  {
    $xfer += $input->readFieldBegin(\$fname, \$ftype, \$fid);
    if ($ftype == TType::STOP) {
      last;
    }
    SWITCH: for($fid)
    {
      /^1$/ && do{      if ($ftype == TType::STRING) {
        $xfer += $input->readString(\$self->{vip});
      } else {
        $xfer += $input->skip($ftype);
      }
      last; };
      /^2$/ && do{      if ($ftype == TType::STRING) {
        $xfer += $input->readString(\$self->{rid});
      } else {
        $xfer += $input->skip($ftype);
      }
      last; };
      /^3$/ && do{      if ($ftype == TType::STRING) {
        $xfer += $input->readString(\$self->{master_ip});
      } else {
        $xfer += $input->skip($ftype);
      }
      last; };
      /^4$/ && do{      if ($ftype == TType::STRING) {
        $xfer += $input->readString(\$self->{backup_ip});
      } else {
        $xfer += $input->skip($ftype);
      }
      last; };
        $xfer += $input->skip($ftype);
    }
    $xfer += $input->readFieldEnd();
  }
  $xfer += $input->readStructEnd();
  return $xfer;
}

sub write {
  my ($self, $output) = @_;
  my $xfer   = 0;
  $xfer += $output->writeStructBegin('NetInfo');
  if (defined $self->{vip}) {
    $xfer += $output->writeFieldBegin('vip', TType::STRING, 1);
    $xfer += $output->writeString($self->{vip});
    $xfer += $output->writeFieldEnd();
  }
  if (defined $self->{rid}) {
    $xfer += $output->writeFieldBegin('rid', TType::STRING, 2);
    $xfer += $output->writeString($self->{rid});
    $xfer += $output->writeFieldEnd();
  }
  if (defined $self->{master_ip}) {
    $xfer += $output->writeFieldBegin('master_ip', TType::STRING, 3);
    $xfer += $output->writeString($self->{master_ip});
    $xfer += $output->writeFieldEnd();
  }
  if (defined $self->{backup_ip}) {
    $xfer += $output->writeFieldBegin('backup_ip', TType::STRING, 4);
    $xfer += $output->writeString($self->{backup_ip});
    $xfer += $output->writeFieldEnd();
  }
  $xfer += $output->writeFieldStop();
  $xfer += $output->writeStructEnd();
  return $xfer;
}

package OVP::IDVHa::DrbdInfo;
use base qw(Class::Accessor);
OVP::IDVHa::DrbdInfo->mk_accessors( qw( res_num port_num primary_host secondary_host block_dev is_external metedata ) );

sub new {
  my $classname = shift;
  my $self      = {};
  my $vals      = shift || {};
  $self->{res_num} = undef;
  $self->{port_num} = undef;
  $self->{primary_host} = undef;
  $self->{secondary_host} = undef;
  $self->{block_dev} = undef;
  $self->{is_external} = undef;
  $self->{metedata} = undef;
  if (UNIVERSAL::isa($vals,'HASH')) {
    if (defined $vals->{res_num}) {
      $self->{res_num} = $vals->{res_num};
    }
    if (defined $vals->{port_num}) {
      $self->{port_num} = $vals->{port_num};
    }
    if (defined $vals->{primary_host}) {
      $self->{primary_host} = $vals->{primary_host};
    }
    if (defined $vals->{secondary_host}) {
      $self->{secondary_host} = $vals->{secondary_host};
    }
    if (defined $vals->{block_dev}) {
      $self->{block_dev} = $vals->{block_dev};
    }
    if (defined $vals->{is_external}) {
      $self->{is_external} = $vals->{is_external};
    }
    if (defined $vals->{metedata}) {
      $self->{metedata} = $vals->{metedata};
    }
  }
  return bless ($self, $classname);
}

sub getName {
  return 'DrbdInfo';
}

sub read {
  my ($self, $input) = @_;
  my $xfer  = 0;
  my $fname;
  my $ftype = 0;
  my $fid   = 0;
  $xfer += $input->readStructBegin(\$fname);
  while (1) 
  {
    $xfer += $input->readFieldBegin(\$fname, \$ftype, \$fid);
    if ($ftype == TType::STOP) {
      last;
    }
    SWITCH: for($fid)
    {
      /^1$/ && do{      if ($ftype == TType::I32) {
        $xfer += $input->readI32(\$self->{res_num});
      } else {
        $xfer += $input->skip($ftype);
      }
      last; };
      /^2$/ && do{      if ($ftype == TType::I32) {
        $xfer += $input->readI32(\$self->{port_num});
      } else {
        $xfer += $input->skip($ftype);
      }
      last; };
      /^3$/ && do{      if ($ftype == TType::STRING) {
        $xfer += $input->readString(\$self->{primary_host});
      } else {
        $xfer += $input->skip($ftype);
      }
      last; };
      /^4$/ && do{      if ($ftype == TType::STRING) {
        $xfer += $input->readString(\$self->{secondary_host});
      } else {
        $xfer += $input->skip($ftype);
      }
      last; };
      /^5$/ && do{      if ($ftype == TType::STRING) {
        $xfer += $input->readString(\$self->{block_dev});
      } else {
        $xfer += $input->skip($ftype);
      }
      last; };
      /^6$/ && do{      if ($ftype == TType::BOOL) {
        $xfer += $input->readBool(\$self->{is_external});
      } else {
        $xfer += $input->skip($ftype);
      }
      last; };
      /^7$/ && do{      if ($ftype == TType::STRING) {
        $xfer += $input->readString(\$self->{metedata});
      } else {
        $xfer += $input->skip($ftype);
      }
      last; };
        $xfer += $input->skip($ftype);
    }
    $xfer += $input->readFieldEnd();
  }
  $xfer += $input->readStructEnd();
  return $xfer;
}

sub write {
  my ($self, $output) = @_;
  my $xfer   = 0;
  $xfer += $output->writeStructBegin('DrbdInfo');
  if (defined $self->{res_num}) {
    $xfer += $output->writeFieldBegin('res_num', TType::I32, 1);
    $xfer += $output->writeI32($self->{res_num});
    $xfer += $output->writeFieldEnd();
  }
  if (defined $self->{port_num}) {
    $xfer += $output->writeFieldBegin('port_num', TType::I32, 2);
    $xfer += $output->writeI32($self->{port_num});
    $xfer += $output->writeFieldEnd();
  }
  if (defined $self->{primary_host}) {
    $xfer += $output->writeFieldBegin('primary_host', TType::STRING, 3);
    $xfer += $output->writeString($self->{primary_host});
    $xfer += $output->writeFieldEnd();
  }
  if (defined $self->{secondary_host}) {
    $xfer += $output->writeFieldBegin('secondary_host', TType::STRING, 4);
    $xfer += $output->writeString($self->{secondary_host});
    $xfer += $output->writeFieldEnd();
  }
  if (defined $self->{block_dev}) {
    $xfer += $output->writeFieldBegin('block_dev', TType::STRING, 5);
    $xfer += $output->writeString($self->{block_dev});
    $xfer += $output->writeFieldEnd();
  }
  if (defined $self->{is_external}) {
    $xfer += $output->writeFieldBegin('is_external', TType::BOOL, 6);
    $xfer += $output->writeBool($self->{is_external});
    $xfer += $output->writeFieldEnd();
  }
  if (defined $self->{metedata}) {
    $xfer += $output->writeFieldBegin('metedata', TType::STRING, 7);
    $xfer += $output->writeString($self->{metedata});
    $xfer += $output->writeFieldEnd();
  }
  $xfer += $output->writeFieldStop();
  $xfer += $output->writeStructEnd();
  return $xfer;
}

package OVP::IDVHa::NodeInfo;
use base qw(Class::Accessor);
OVP::IDVHa::NodeInfo->mk_accessors( qw( hostname ) );

sub new {
  my $classname = shift;
  my $self      = {};
  my $vals      = shift || {};
  $self->{hostname} = undef;
  if (UNIVERSAL::isa($vals,'HASH')) {
    if (defined $vals->{hostname}) {
      $self->{hostname} = $vals->{hostname};
    }
  }
  return bless ($self, $classname);
}

sub getName {
  return 'NodeInfo';
}

sub read {
  my ($self, $input) = @_;
  my $xfer  = 0;
  my $fname;
  my $ftype = 0;
  my $fid   = 0;
  $xfer += $input->readStructBegin(\$fname);
  while (1) 
  {
    $xfer += $input->readFieldBegin(\$fname, \$ftype, \$fid);
    if ($ftype == TType::STOP) {
      last;
    }
    SWITCH: for($fid)
    {
      /^1$/ && do{      if ($ftype == TType::STRING) {
        $xfer += $input->readString(\$self->{hostname});
      } else {
        $xfer += $input->skip($ftype);
      }
      last; };
        $xfer += $input->skip($ftype);
    }
    $xfer += $input->readFieldEnd();
  }
  $xfer += $input->readStructEnd();
  return $xfer;
}

sub write {
  my ($self, $output) = @_;
  my $xfer   = 0;
  $xfer += $output->writeStructBegin('NodeInfo');
  if (defined $self->{hostname}) {
    $xfer += $output->writeFieldBegin('hostname', TType::STRING, 1);
    $xfer += $output->writeString($self->{hostname});
    $xfer += $output->writeFieldEnd();
  }
  $xfer += $output->writeFieldStop();
  $xfer += $output->writeStructEnd();
  return $xfer;
}

1;
