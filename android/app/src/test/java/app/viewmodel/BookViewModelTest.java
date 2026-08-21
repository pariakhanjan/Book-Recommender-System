package app.viewmodel;

import static org.junit.Assert.assertNotNull;
import androidx.arch.core.executor.testing.InstantTaskExecutorRule;
import com.bookrecommender.app.viewmodel.BookViewModel;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.mockito.MockitoAnnotations;

public class BookViewModelTest {
    @Rule public InstantTaskExecutorRule instantTaskExecutorRule = new InstantTaskExecutorRule();
    private BookViewModel viewModel;

    @Before
    public void setUp() {
        MockitoAnnotations.openMocks(this);
        viewModel = new BookViewModel();
    }

    @Test
    public void testViewModelInitialization() {
        assertNotNull(viewModel.getBooks());
        assertNotNull(viewModel.getIsLoading());
    }
}