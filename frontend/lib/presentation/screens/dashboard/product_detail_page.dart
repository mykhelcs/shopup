import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../services/cart_provider.dart';

class ProductDetailPage extends StatelessWidget {
  final String id;
  final String name;
  final double price;

  const ProductDetailPage({
    super.key, 
    this.id = 'p0',
    this.name = "Product", 
    this.price = 0
  });

  @override
  Widget build(BuildContext context) {
    final cartProvider = Provider.of<CartProvider>(context, listen: false);

    return Scaffold(
      appBar: AppBar(title: Text(name)),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Container(
              height: 200,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Center(child: Icon(Icons.image, size: 80, color: Colors.grey)),
            ),
            const SizedBox(height: 20),
            Text(name, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            Text("\$${price.toStringAsFixed(2)}", style: const TextStyle(fontSize: 20, color: Color(0xFFFF6B35), fontWeight: FontWeight.bold)),
            const SizedBox(height: 40),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  cartProvider.addItem(id, name, price);
                  ScaffoldMessenger.of(context).hideCurrentSnackBar();
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text("Added to cart!"),
                      duration: Duration(seconds: 1),
                      backgroundColor: Color(0xFF36454F),
                    ),
                  );
                },
                child: const Text("Add to Cart"),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
