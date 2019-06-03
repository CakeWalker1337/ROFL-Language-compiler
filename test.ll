


define i32 @main() {
    %i.ptr = alloca i32
    store i32 0, i32* %i.ptr
    br label %lab.0
lab.0:
    %i.1 = load i32, i32* %i.ptr
    %buffer2 = icmp slt i32 %i.1, 30
    br i1 %buffer2, label %lab.1, label %lab.2
lab.1:
    %i.3 = load i32, i32* %i.ptr
    %buffer4 = add i32 %i.3, 3
    store i32 %buffer4, i32* %i.ptr
    %buffer5 = load i32, i32* %i.ptr
    %buffer6 = load i32, i32* %i.ptr
    %buffer7 = getelementptr inbounds [13 x i8], [13 x i8]* @.str.2, i32 0, i32 0 
    call i32 (i8*, ...) @printf(i8* %buffer7, i32 %buffer5, i32 %buffer6)
    br label %lab.0
lab.2:
    ret i32 0
}

declare i32 @printf(i8*, ...)
@.str.1 = private unnamed_addr constant [8 x i8] c"iter - \00", align 1
@.str.2 = private unnamed_addr constant [13 x i8] c"%diter - %d\0A\00", align 1
