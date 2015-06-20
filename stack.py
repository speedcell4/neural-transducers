import theano
import theano.tensor as T
import numpy         as np
from theano.printing import Print
from theano_toolkit import utils as U
from theano_toolkit.parameters import Parameters


def build(size):
    def init(sequence_length):
        initial_V = T.alloc(np.float32(0),sequence_length,size)
        initial_s = T.alloc(np.float32(0),sequence_length)
        def step(t,v,d,u,prev_V,prev_s):
            prev_V = prev_V[:t]
            prev_s = prev_s[:t]
            V = T.concatenate([
                prev_V,
                v.dimshuffle('x',0),
                initial_V[t+1:]
            ])

            rev_cum_prev_s = T.cumsum(prev_s[::-1])[::-1]
            to_flip_ = u - rev_cum_prev_s
            to_flip = (to_flip_ > 0) * to_flip_
            new_s_ = prev_s - to_flip
            new_s = (new_s_ > 0) * new_s_
            s = T.concatenate([
                new_s,
                d.dimshuffle('x'),
                initial_s[t+1:]
            ])

            rev_cum_s = T.cumsum(new_s[::-1])[::-1] + d
            flip_score_ = 1 - rev_cum_s
            flip_score = (flip_score_ > 0) * flip_score_
            score = T.min([new_s,flip_score],axis=0)

            r = T.dot(score,prev_V) + d * v

            return V,s,r
        return initial_V,initial_s,step
    return init


if __name__ == "__main__":
    t = T.iscalar('t')
    v = T.vector('v')
    d = T.scalar('d')
    u = T.scalar('u')

    stack_init = build(5)

    initial_V,initial_s,step = stack_init(10)

    V,s,r = step(
            t = t, v = v, d = d, u = u,
            prev_V = initial_V,
            prev_s = initial_s
        )

    f = theano.function(
            inputs = [t,v,d,u],
            outputs = [V,s,r]
        )

    V,s,r = f(
        np.int32(0),
        np.random.randn(5).astype(np.float32),
        np.float32(0.),
        np.float32(1.),
    )

    print V
    print s
    print r


