      // Function to open the modal when "View" button is clicked
      document.querySelectorAll('.view-product').forEach(item => {
        item.addEventListener('click', event => {
            var imageUrl = item.getAttribute('data-image');
            var modal = document.getElementById("myModal");
            var modalImage = document.getElementById("modal-image");
            modalImage.src = imageUrl;
            modal.style.display = "block";

            // Function to close the modal
            var closeBtn = document.getElementsByClassName("close")[0];
            closeBtn.onclick = function() {
                modal.style.display = "none";
            }

            // Function to close the modal when clicking outside of it
            window.onclick = function(event) {
                if (event.target == modal) {
                    modal.style.display = "none";
                }
            }
        });
    });