import grpc

DEFAULT_GRPC_TARGET = "sa-api.twopercents.svc.cluster.local:8090"


def channel(target: str = DEFAULT_GRPC_TARGET):
    if target.endswith(":443"):
        channel = grpc.secure_channel(
            target,
            grpc.ssl_channel_credentials(),
        )
    else:
        channel = grpc.insecure_channel(target)

    return channel
