package dk.magenta.mox.agent;

import com.rabbitmq.client.AMQP;
import com.rabbitmq.client.QueueingConsumer;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;
import java.util.concurrent.TimeoutException;

public class MessageReceiver extends MessageInterface {

    private QueueingConsumer consumer;
    private boolean running;
    private boolean sendReplies;

    public MessageReceiver(String host, String exchange, String queue, boolean sendReplies) throws IOException, TimeoutException {
        super(host, exchange, queue);
        this.consumer = new QueueingConsumer(this.getChannel());
        this.getChannel().basicConsume(queue, true, this.consumer);
        this.sendReplies = sendReplies;
    }

    public void run(MessageHandler callback) throws InterruptedException {
        this.running = true;
        while (this.running) {
            QueueingConsumer.Delivery delivery = this.consumer.nextDelivery();

            try {
                final Future<String> response = callback.run(delivery.getProperties().getHeaders(), new JSONObject(new String(delivery.getBody())));

                if (this.sendReplies && response != null) {
                    final AMQP.BasicProperties deliveryProperties = delivery.getProperties();
                    final AMQP.BasicProperties responseProperties = new AMQP.BasicProperties().builder().correlationId(deliveryProperties.getCorrelationId()).build();

                    // Wait for a response from the callback and send it back to the original message sender
                    new Thread(new Runnable() {
                        public void run() {
                            try {
                                String responseString = response.get(); // This blocks while we wait for the callback to run. Hence the thread
                                MessageReceiver.this.getChannel().basicPublish("", deliveryProperties.getReplyTo(), responseProperties, responseString.getBytes());
                            } catch (InterruptedException e) {
                                e.printStackTrace();
                            } catch (ExecutionException e) {
                                e.printStackTrace();
                            } catch (IOException e) {
                                e.printStackTrace();
                            }
                        }
                    }).start();
                }

            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
    }

    public void stop() {
        this.running = false;
    }
}
