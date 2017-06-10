import tensorflow as tf
from general.tf.planning.cost.cost import Cost

# TODO make this better
class CostColl(Cost):
    """Cost for collision.
    """

    def __init__(self, params):
        self.weight = tf.constant(params['weight'])
        if params['cost'] == "square":
            self.cost = tf.square
        else:
            raise NotImplementedError(
                "CostColl {0} is not valid".format(cost))

    def eval(self, probcoll, data):
        components = self.cost(data) * probcoll
        weighted_sum = tf.reduce_sum(components * self.weight, axis=(1, 2))
        return weighted_sum
