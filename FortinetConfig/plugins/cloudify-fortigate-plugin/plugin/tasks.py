from cloudify.decorators import operation
from cloudify import ctx
from cloudify.state import ctx_parameters as inputs
import paramiko


def exec_command(ctx, command):

    username = inputs['username']
    password = inputs['password']

    fortigate_host_ip = ctx.instance.host_ip
    ctx.logger.info('HOST_IP: {0}'.format(ctx.instance.host_ip))

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(fortigate_host_ip, username=username,password=password)

    stdin, stdout, stderr = ssh.exec_command(command)
    ctx.logger.info('Exit status >> {0}'.format(stdout.channel.recv_exit_status()))

    ssh.close



## Loop over relationships with 'connected_to_port' and assign the fixed ip to the relevant port
## the order of the port a based on the relationships order

@operation
def config_ports(ctx, **kwargs):

    ctx.logger.info('Start port config task....')
    portId = 2  # port 1 reserved for admin
    portMask = '255.255.255.0'

    for relationship in ctx.instance.relationships:

        ctx.logger.info('RELATIONSHIP type : {0}'.format(relationship.type))

        if 'connected_to_port' in relationship.type:
            target_ip = relationship.target.instance.runtime_properties['fixed_ip_address']
            ctx.logger.info('TARGET IP target_ip : {0}'.format(target_ip))

            command = \
                'config system interface\n' \
                '  edit port%s\n' \
                '    set mode static\n' \
                '    set ip %s %s\n' \
                'end' % (portId, target_ip, portMask)

            exec_command(ctx, command)

            portId += 1

        if 'connected_to' in relationship.type:

            portId += 1


@operation
def create_policy(ctx, **kwargs):

    ctx.logger.info('Start FW policy configuration....')

    policyId = inputs['policyId']
    policyName = inputs['policyName']
    srcintf = inputs['srcintf']
    dstintf = inputs['dstintf']
    action = inputs['action']
    serviceName = inputs['serviceName']

    command = \
        'config firewall policy\n' \
        '  edit %s\n' \
        '    set name %s\n' \
        '    set srcintf %s\n' \
        '    set dstintf %s\n' \
        '    set srcaddr all\n' \
        '    set dstaddr all\n' \
        '    set action %s\n' \
        '    set schedule always\n' \
        '    set service \"%s\"\n' \
        'end' % (policyId, policyName, srcintf, dstintf, action, serviceName)

    ctx.logger.info('Execute Command >> \n {0}'.format(command))

    exec_command(ctx, command)


@operation
def create_service(ctx, **kwargs):

    ctx.logger.info('Start FW service creation....')

    protocol = inputs['protocol']
    portrange = inputs['portrange']
    serviceName = inputs['serviceName']

    command = \
        'config firewall service custom\n' \
        '   edit %s\n' \
        '       set protocol \"%s\"\n' \
        '       set tcp-portrange %s\n' \
        'end' % (serviceName, protocol, portrange)

    ctx.logger.info('Execute Command >> \n {0}'.format(command))

    exec_command(ctx, command)

